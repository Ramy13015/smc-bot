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
    TradingView webhook endpoint for processing trading signals
    
    Process:
    1. Parse and validate JSON payload
    2. Check for duplicate signals
    3. Calculate SMC confluence score
    4. Validate critical flags
    5. Calculate risk management parameters
    6. Send Telegram notification if score meets threshold
    
    Returns:
        200: Signal processed and sent
        202: Signal received but not sent (duplicate/below threshold/invalid)
        400: Invalid JSON
        422: Validation error
    """
    request_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(request)}"
    logger.info(f"[{request_id}] Webhook received")
    
    # Parse JSON payload
    try:
        raw_payload = await request.json()
        logger.debug(f"[{request_id}] Raw payload: {raw_payload}")
    except Exception as e:
        logger.error(f"[{request_id}] JSON parse error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON format"
        )
    
    # Validate with Pydantic
    try:
        payload = TVPayload(**raw_payload)
        logger.info(
            f"[{request_id}] Valid payload: {payload.symbol} {payload.direction} "
            f"@ {payload.price_ctx.entry}"
        )
    except ValidationError as e:
        logger.error(f"[{request_id}] Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.errors()
        )
    
    # Check for duplicates
    event_id = payload.event_id
    if is_duplicate(event_id, Config.ANTI_SPAM_TTL):
        logger.info(f"[{request_id}] Duplicate signal: {event_id}")
        return JSONResponse(
            status_code=202,
            content={
                "ok": True,
                "score": 0,
                "sent": False,
                "reason": "duplicate_suppressed",
                "event_id": event_id
            }
        )
    
    # Calculate confluence score
    score = calculate_confluence_score(payload.flags)
    logger.info(f"[{request_id}] Confluence score: {score:.2f} (threshold: {Config.CONFLUENCE_THRESH})")
    
    # Validate critical flags
    flags_valid, invalid_reason = validate_critical_flags(payload.flags)
    if not flags_valid:
        logger.warning(f"[{request_id}] Critical flags missing: {invalid_reason}")
        return JSONResponse(
            status_code=202,
            content={
                "ok": True,
                "score": score,
                "sent": False,
                "reason": invalid_reason,
                "event_id": event_id
            }
        )
    
    # Check score threshold
    if score < Config.CONFLUENCE_THRESH:
        logger.info(f"[{request_id}] Score below threshold: {score} < {Config.CONFLUENCE_THRESH}")
        return JSONResponse(
            status_code=202,
            content={
                "ok": True,
                "score": score,
                "sent": False,
                "reason": "below_threshold",
                "event_id": event_id
            }
        )
    
    # Calculate risk management parameters
    try:
        entry, sl, tp, position_size = calculate_risk_parameters(
            payload=payload,
            base_equity=Config.BASE_EQUITY,
            risk_pct=Config.RISK_PCT,
            atr_sl_mult=Config.ATR_SL_MULT,
            atr_tp_mult=Config.ATR_TP_MULT
        )
        
        rr_ratio = calculate_rr_ratio(entry, sl, tp)
        
        logger.info(
            f"[{request_id}] Trade params: Entry={entry}, SL={sl}, TP={tp}, "
            f"Size={position_size}, R:R=1:{rr_ratio}"
        )
    except Exception as e:
        logger.error(f"[{request_id}] Risk calculation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error calculating trade parameters"
        )
    
    # Get active flags
    active_flags = get_active_flags(payload.flags)
    
    # Format Telegram message
    message = format_telegram_message(
        score=score,
        symbol=payload.symbol,
        timeframe=payload.timeframe,
        direction=payload.direction,
        entry=entry,
        sl=sl,
        tp=tp,
        position_size=position_size,
        rr_ratio=rr_ratio,
        flags=active_flags
    )
    
    # Send Telegram notification
    telegram_success = send_telegram_message(
        message=message,
        token=Config.TELEGRAM_TOKEN,
        chat_id=Config.TELEGRAM_CHAT_ID
    )
    
    if telegram_success:
        logger.info(f"[{request_id}] Signal sent successfully: {event_id}")
        return JSONResponse(
            status_code=200,
            content={
                "ok": True,
                "score": score,
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
        logger.error(f"[{request_id}] Telegram send failed: {event_id}")
        return JSONResponse(
            status_code=202,
            content={
                "ok": True,
                "score": score,
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