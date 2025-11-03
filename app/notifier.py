"""
Telegram notification functions using httpx
"""
import httpx
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
            with httpx.Client(timeout=10.0) as client:
                response = client.post(url, json=payload)
                
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