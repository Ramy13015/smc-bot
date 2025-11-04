"""
FastAPI main application for SMC Trading Bot
Version: 2.0.10 - CONFLUENCE 10% TEST
"""
import logging
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import uvicorn

from app.models import TVPayload
from app.config import Config
from app.smc import (
    calculate_confluence_score,
    validate_critical_flags,
    calculate_risk_parameters,
    calculate_rr_ratio,
    get_active_flags
)
from app.notifier import send_telegram_message, format_telegram_message
from app.utils import is_duplicate, get_cache_size, clear_cache

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="SMC Trading Bot - HIGH VOLUME MARKETS",
    version="2.0.0",
    description="SMC Bot for High Volume FOREX & CRYPTO PERPETUALS"
)

# Supported symbols - HIGH VOLUME/LIQUIDITY ONLY
SUPPORTED_SYMBOLS = {
    # FOREX - Major pairs + Gold (high volume)
    "EURUSD": "forex",
    "GBPUSD": "forex", 
    "USDJPY": "forex",
    "AUDUSD": "forex",
    "USDCAD": "forex",
    "XAUUSD": "gold",
    
    # CRYPTO PERPETUALS - Top volume/volatility
    "BTCUSDT.P": "crypto",
    "ETHUSDT.P": "crypto",
    "SOLUSDT.P": "crypto",
    "ADAUSDT.P": "crypto",
    "DOGEUSDT.P": "crypto",
    "XRPUSDT.P": "crypto"
}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "status": "running",
        "bot": "SMC Trading Bot - HIGH VOLUME MARKETS",
        "version": "2.0.0",
        "focus": "High volume FOREX & CRYPTO PERPETUALS",
        "supported_symbols": list(SUPPORTED_SYMBOLS.keys()),
        "market_types": {
            "forex": [k for k, v in SUPPORTED_SYMBOLS.items() if v == "forex"],
            "crypto_perpetuals": [k for k, v in SUPPORTED_SYMBOLS.items() if v == "crypto"],
            "gold": [k for k, v in SUPPORTED_SYMBOLS.items() if v == "gold"]
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "ok": True,
        "timestamp": datetime.now().isoformat(),
        "supported_markets": {
            "forex_majors": ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD"],
            "crypto_perpetuals": ["BTCUSDT.P", "ETHUSDT.P", "SOLUSDT.P", "ADAUSDT.P", "DOGEUSDT.P", "XRPUSDT.P"],
            "precious_metals": ["XAUUSD"]
        },
        "config": {
            "telegram_configured": bool(Config.TELEGRAM_TOKEN and Config.TELEGRAM_CHAT_ID),
            "confluence_threshold": Config.CONFLUENCE_THRESH,
            "risk_pct": Config.RISK_PCT,
            "focus": "HIGH VOLUME MARKETS ONLY"
        },
        "cache_size": get_cache_size()
    }


@app.post("/tv")
async def tradingview_webhook(request: Request):
    """
    TradingView webhook - DIRECT RELAY MODE
    
    Pine Script calcule TOUT (entry, sl, tp).
    Le bot Python ne fait que relayer vers Telegram.
    
    Returns:
        200: Signal sent
        400: Invalid JSON
    """
    request_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(request)}"
    logger.info(f"[{request_id}] Webhook received")
    
    # Parse JSON payload
    try:
        data = await request.json()
        logger.info(f"[{request_id}] Pine Script data: {data}")
    except Exception as e:
        logger.error(f"[{request_id}] JSON parse error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON format"
        )
    
    # Extract data (Pine Script a TOUT calculé)
    event_id = data.get("event_id")
    symbol = data.get("symbol")
    direction = data.get("direction")
    entry = data.get("entry")
    sl = data.get("sl")
    tp = data.get("tp")
    atr = data.get("atr")
    poi_valid = data.get("poi_valid", False)
    fvg_open = data.get("fvg_open", False)
    ob_valid = data.get("ob_valid", False)
    
    logger.info(
        f"[{request_id}] PINE SCRIPT DATA: {symbol} {direction} "
        f"Entry={entry} SL={sl} TP={tp} ATR={atr}"
    )
    
    # Check for duplicates
    if is_duplicate(event_id, Config.ANTI_SPAM_TTL):
        logger.info(f"[{request_id}] Duplicate signal: {event_id}")
        return JSONResponse(
            status_code=202,
            content={
                "ok": True,
                "sent": False,
                "reason": "duplicate",
                "event_id": event_id
            }
        )
    
    # Calculate Risk:Reward ratio
    rr_ratio = calculate_rr_ratio(entry, sl, tp)
    
    # Calculate position size (only thing we calculate)
    risk_amount = Config.BASE_EQUITY * Config.RISK_PCT
    price_distance = abs(entry - sl)
    position_size = risk_amount / price_distance if price_distance > 0 else 0
    
    # Active flags for display
    active_flags = []
    if poi_valid:
        active_flags.append("POI Valid")
    if fvg_open:
        active_flags.append("FVG Open")
    if ob_valid:
        active_flags.append("OB Valid")
    
    # Format message (simplifié)
    direction_emoji = "🟢" if direction == "LONG" else "🔴"
    message = f"""{direction_emoji} **SMC SIGNAL - {direction} {symbol}**

💰 **Entry:** `{entry:.5f}`
🛑 **Stop Loss:** `{sl:.5f}`
🎯 **Take Profit:** `{tp:.5f}`
📏 **Position Size:** `{position_size:.2f}`
⚖️ **Risk:Reward:** `1:{rr_ratio:.2f}`
📊 **ATR:** `{atr:.2f}`

🎯 **Flags:** {', '.join(active_flags) if active_flags else 'None'}

📢 *@MonBotFibo*"""
    
    # Send Telegram notification
    telegram_success = send_telegram_message(
        message=message,
        token=Config.TELEGRAM_TOKEN,
        chat_id=Config.TELEGRAM_CHAT_ID
    )
    
    if telegram_success:
        logger.info(f"[{request_id}] ✅ SIGNAL SENT: {event_id}")
        return JSONResponse(
            status_code=200,
            content={
                "ok": True,
                "sent": True,
                "event_id": event_id,
                "trade": {
                    "entry": entry,
                    "sl": sl,
                    "tp": tp,
                    "size": position_size,
                    "rr": rr_ratio
                }
            }
        )
    else:
        logger.error(f"[{request_id}] ❌ TELEGRAM FAILED: {event_id}")
        return JSONResponse(
            status_code=202,
            content={
                "ok": True,
                "sent": False,
                "reason": "telegram_error",
                "event_id": event_id
            }
        )


@app.get("/stats")
async def get_stats():
    """Get bot statistics"""
    return {
        "cache_size": get_cache_size(),
        "config": {
            "confluence_threshold": Config.CONFLUENCE_THRESH,
            "risk_pct": Config.RISK_PCT,
            "atr_sl_mult": Config.ATR_SL_MULT,
            "atr_tp_mult": Config.ATR_TP_MULT
        }
    }


@app.post("/clear-cache")
async def admin_clear_cache():
    """Clear duplicate detection cache"""
    clear_cache()
    logger.info("Cache cleared manually")
    return {"ok": True, "message": "Cache cleared"}


if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", "8000"))
    logger.info(f"Starting SMC Bot on port {port}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )