"""
Telegram notification functions using requests
"""
import requests
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


def format_telegram_message(
    score: float,
    symbol: str,
    timeframe: str,
    direction: str,
    entry: float,
    sl: float,
    tp: float,
    position_size: float,
    rr_ratio: float,
    flags: List[str]
) -> str:
    """
    Format trading signal for Telegram message
    
    Args:
        score: Confluence score
        symbol: Trading symbol
        timeframe: Chart timeframe
        direction: Trade direction
        entry: Entry price
        sl: Stop loss price
        tp: Take profit price
        position_size: Position size
        rr_ratio: Risk:Reward ratio
        flags: List of active flags
        
    Returns:
        Formatted Telegram message
    """
    direction_emoji = "🟢" if direction == "LONG" else "🔴"
    
    message = f"""
{direction_emoji} **SMC SIGNAL - {direction} {symbol}**

📊 **Confluence Score:** `{score:.1%}`
📈 **Timeframe:** `{timeframe}`
💰 **Entry:** `{entry:.5f}`
🛑 **Stop Loss:** `{sl:.5f}`
🎯 **Take Profit:** `{tp:.5f}`
📏 **Position Size:** `{position_size:.2f}`
⚖️ **Risk:Reward:** `1:{rr_ratio:.2f}`

🎯 **Active Flags:**
{chr(10).join([f"✅ {flag}" for flag in flags])}

📢 *@MonBotFibo*
    """.strip()
    
    return message


def send_telegram_message(
    message: str,
    token: Optional[str],
    chat_id: Optional[str],
    max_retries: int = 2
) -> bool:
    """
    Send message to Telegram with retry logic
    
    Args:
        message: Message to send
        token: Telegram bot token
        chat_id: Telegram chat ID
        max_retries: Maximum retry attempts
        
    Returns:
        True if successful, False otherwise
    """
    if not token or not chat_id:
        logger.error("Telegram token or chat_id not configured")
        return False
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    for attempt in range(max_retries + 1):
        try:
            response = requests.post(url, json=payload, timeout=10.0)
            
            if response.status_code == 200:
                logger.info("Telegram message sent successfully")
                return True
            else:
                logger.warning(f"Telegram API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Telegram send attempt {attempt + 1} failed: {e}")
            
        if attempt < max_retries:
            logger.info(f"Retrying Telegram send... ({attempt + 1}/{max_retries})")
    
    logger.error("Failed to send Telegram message after all retries")
    return False


def send_smc_ai_signal(
    trade_data: dict,
    ai_trade: dict,
    confluence_score: float,
    timeframe: str,
    active_flags: List[str],
    token: Optional[str],
    chat_id: Optional[str]
) -> bool:
    """
    Send enhanced SMC signal with GROK + DEEPSEEK advice
    
    Args:
        trade_data: Original trade data from Pine Script
        ai_trade: AI-enhanced trade data with advice
        confluence_score: Confluence percentage
        timeframe: Chart timeframe 
        active_flags: List of active SMC flags
        token: Telegram bot token
        chat_id: Telegram chat ID
        
    Returns:
        True if successful, False otherwise
    """
    # Format timeframe display
    tf_display = timeframe
    if timeframe == "5":
        tf_display = "5min"
    elif timeframe == "15":
        tf_display = "15min"
    elif timeframe == "60":
        tf_display = "1h"
    elif timeframe == "240":
        tf_display = "4h"
    
    # Format flags display
    flags_text = "\n".join([f"• {flag.replace('✅ ', '').replace('_', ' ').title()}" for flag in active_flags])
    
    # Direction emoji
    direction_emoji = "🟢" if ai_trade["direction"] == "LONG" else "🔴"
    
    # Calculate position size for display
    risk_amount = 5000 * 0.01  # BASE_EQUITY * RISK_PCT
    price_distance = abs(ai_trade["entry"] - ai_trade["sl"])
    position_size = risk_amount / price_distance if price_distance > 0 else 0.04
    
    # Build the premium notification message
    message = f"""🎯 *SMC SIGNAL - {ai_trade["direction"]} {ai_trade["symbol"]}*

📊 *Confluence Score:* {confluence_score:.1f}%
📈 *Timeframe:* {tf_display}
💰 *Entry:* {ai_trade["entry"]:.2f}
🛑 *Stop Loss:* {ai_trade["sl"]:.2f}
🎯 *Take Profit:* {ai_trade["tp"]:.2f}
📏 *Position Size:* {position_size:.2f}
⚖️ *Risk:Reward:* 1:{ai_trade["risk_reward"]:.2f}

*Active Flags:*
{flags_text}

🤖 *GROK (Stratégiste):*
{ai_trade.get("grok_advice", "Signal validé par IA")}
*Conseil:* SL à {ai_trade["sl"]:.0f} (ATR 1.5x), TP à {ai_trade["tp"]:.0f} (R:R {ai_trade["risk_reward"]:.1f})

🧠 *DEEPSEEK (Risk Manager):*
{ai_trade.get("deepseek_advice", "SL/TP optimisés par IA")}
*Conseil:* {position_size:.2f} lot (1% risque), trailing stop à +1.5%

📢 *@MonBotFibo*
    """.strip()
    
    return send_telegram_message(message, token, chat_id)