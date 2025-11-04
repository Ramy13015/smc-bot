"""
Configuration management using environment variables
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for SMC Trading Bot"""
    
    # Telegram Configuration
    TELEGRAM_TOKEN: Optional[str] = os.getenv("TELEGRAM_TOKEN")
    TELEGRAM_CHAT_ID: Optional[str] = os.getenv("TELEGRAM_CHAT_ID")
    
    # Trading Parameters
    BASE_EQUITY: float = float(os.getenv("BASE_EQUITY", "5000"))
    RISK_PCT: float = float(os.getenv("RISK_PCT", "0.01"))
    # CONFLUENCE À 76% - HIGH QUALITY SIGNALS (8+ flags minimum)
    CONFLUENCE_THRESH: float = 0.76  # 76% minimum pour des signaux de haute qualité
    
    # Risk Management
    ATR_SL_MULT: float = float(os.getenv("ATR_SL_MULT", "1.5"))
    ATR_TP_MULT: float = float(os.getenv("ATR_TP_MULT", "2.0"))
    
    # Anti-duplicate
    ANTI_SPAM_TTL: int = int(os.getenv("ANTI_SPAM_TTL", "300"))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        if not cls.TELEGRAM_TOKEN:
            raise ValueError("TELEGRAM_TOKEN is required")
        if not cls.TELEGRAM_CHAT_ID:
            raise ValueError("TELEGRAM_CHAT_ID is required")
        return True