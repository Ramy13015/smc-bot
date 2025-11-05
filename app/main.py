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
from app.notifier import send_telegram_message, format_telegram_message, send_smc_ai_signal
from app.utils import is_duplicate, get_cache_size, clear_cache
from app.smc_ai import process_with_ai

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
    raw_symbol = data.get("symbol")
    # NETTOYAGE SYMBOLE (backup si Pine Script oublie)
    symbol = raw_symbol.replace("BYBIT:", "").replace("BINANCE:", "")
    timeframe = data.get("timeframe", "Unknown")  # 5, 15, 60, 240, etc.
    direction = data.get("direction")
    entry = data.get("entry")
    sl = data.get("sl")
    tp = data.get("tp")
    atr = data.get("atr")
    
    # Extract ALL flags for confluence calculation
    poi_valid = data.get("poi_valid", False)
    fvg_open = data.get("fvg_open", False)
    ob_valid = data.get("ob_valid", False)
    bos_confirm = data.get("bos_confirm", False)
    choch_confirm = data.get("choch_confirm", False)
    liq_swept = data.get("liq_swept", False)
    imbalance_filled = data.get("imbalance_filled", False)
    trend_aligned = data.get("trend_aligned", False)
    volume_confirm = data.get("volume_confirm", False)
    time_filter = data.get("time_filter", False)
    
    logger.info(
        f"[{request_id}] PINE SCRIPT DATA: {symbol} [{timeframe}] {direction} "
        f"Entry={entry} SL={sl} TP={tp} ATR={atr}"
    )
    
    # Calculate confluence score FIRST (before duplicate check)
    flag_count = sum([poi_valid, fvg_open, ob_valid, bos_confirm, choch_confirm, 
                      liq_swept, imbalance_filled, trend_aligned, volume_confirm, time_filter])
    confluence_score = (flag_count / 10.0) * 100
    
    logger.info(f"[{request_id}] Confluence: {confluence_score:.1f}% (threshold: {Config.CONFLUENCE_THRESH*100:.0f}%)")
    
    # Check confluence threshold (>= pour inclure exactement 70%)
    if confluence_score < (Config.CONFLUENCE_THRESH * 100) - 0.01:  # -0.01 pour éviter les erreurs de floating point
        logger.info(f"[{request_id}] Below threshold - Signal rejected")
        return JSONResponse(
            status_code=202,
            content={
                "ok": True,
                "sent": False,
                "reason": "below_threshold",
                "confluence": confluence_score,
                "event_id": event_id
            }
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
    
    # AI VALIDATION with GROK + DEEPSEEK
    signal_data = {
        "symbol": symbol,
        "direction": direction,
        "price_ctx": {
            "entry": entry,
            "sl": sl,
            "tp": tp
        },
        "confluence_score": confluence_score,
        "flags": {
            "poi_valid": poi_valid,
            "fvg_open": fvg_open,
            "ob_valid": ob_valid,
            "bos_confirm": bos_confirm,
            "choch_confirm": choch_confirm,
            "liq_swept": liq_swept,
            "imbalance_filled": imbalance_filled,
            "trend_aligned": trend_aligned,
            "volume_confirm": volume_confirm,
            "time_filter": time_filter
        }
    }
    
    ai_trade = process_with_ai(signal_data)
    if ai_trade:
        logger.info(f"[{request_id}] AI APPROVED: {ai_trade}")
        # Use AI-calculated SL/TP if available
        if ai_trade.get("sl"):
            sl = ai_trade["sl"]
        if ai_trade.get("tp"):
            tp = ai_trade["tp"]
    else:
        logger.info(f"[{request_id}] AI REJECTED signal")
        return JSONResponse(
            status_code=202,
            content={
                "ok": True,
                "sent": False,
                "reason": "ai_rejected",
                "event_id": event_id
            }
        )
    
    # Calculate Risk:Reward ratio
    rr_ratio = calculate_rr_ratio(entry, sl, tp)
    
    # Calculate position size (only thing we calculate)
    risk_amount = Config.BASE_EQUITY * Config.RISK_PCT
    price_distance = abs(entry - sl)
    position_size = risk_amount / price_distance if price_distance > 0 else 0
    
    # Build active flags list with ALL SMC indicators
    active_flags = []
    if poi_valid:
        active_flags.append("✅ Poi Valid")
    if fvg_open:
        active_flags.append("✅ Fvg Open")
    if ob_valid:
        active_flags.append("✅ Ob Valid")
    if bos_confirm:
        active_flags.append("✅ Bos Confirm")
    if choch_confirm:
        active_flags.append("✅ Choch Confirm")
    if liq_swept:
        active_flags.append("✅ Liq Swept")
    if imbalance_filled:
        active_flags.append("✅ Imbalance Filled")
    if trend_aligned:
        active_flags.append("✅ Trend Aligned")
    if volume_confirm:
        active_flags.append("✅ Volume Confirm")
    if time_filter:
        active_flags.append("✅ Time Filter")
    
    # Build original trade data for compatibility
    original_trade_data = {
        "symbol": symbol,
        "direction": direction,
        "entry": entry,
        "sl": sl,
        "tp": tp,
        "timeframe": timeframe
    }
    
    # Send enhanced AI notification
    telegram_success = send_smc_ai_signal(
        trade_data=original_trade_data,
        ai_trade=ai_trade,
        confluence_score=confluence_score,
        timeframe=timeframe,
        active_flags=active_flags,
        token=Config.TELEGRAM_TOKEN,
        chat_id=Config.TELEGRAM_CHAT_ID
    )
    
    if telegram_success:
        logger.info(f"[{request_id}] ✅ SIGNAL SENT: {event_id}")
        return JSONResponse(
            status_code=200,
            content={
                "status": "AI APPROVED",
                "ok": True,
                "sent": True,
                "event_id": event_id,
                "trade": ai_trade if ai_trade else {
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