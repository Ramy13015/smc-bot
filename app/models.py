"""
Pydantic models for TradingView webhook data validation
"""
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict


class Flags(BaseModel):
    """SMC confluence flags for signal validation"""
    model_config = ConfigDict(extra='forbid')
    
    poi_valid: bool = Field(default=False, description="Point of Interest validity")
    fvg_open: bool = Field(default=False, description="Fair Value Gap open")
    ob_valid: bool = Field(default=False, description="Order Block validity") 
    bos_confirm: bool = Field(default=False, description="Break of Structure confirmation")
    choch_confirm: bool = Field(default=False, description="Change of Character confirmation")
    liq_swept: bool = Field(default=False, description="Liquidity swept")
    imbalance_filled: bool = Field(default=False, description="Imbalance filled")
    trend_aligned: bool = Field(default=False, description="Trend alignment")
    volume_confirm: bool = Field(default=False, description="Volume confirmation")
    time_filter: bool = Field(default=False, description="Time filter validation")


class PriceCtx(BaseModel):
    """Price context for trade entry and levels"""
    model_config = ConfigDict(extra='forbid')
    
    entry: float = Field(description="Entry price level")
    ref_high: float = Field(description="Reference high for calculations")
    ref_low: float = Field(description="Reference low for calculations")


class TVPayload(BaseModel):
    """TradingView webhook payload structure"""
    model_config = ConfigDict(extra='forbid')
    
    event_id: str = Field(description="Unique event identifier")
    symbol: str = Field(description="Trading symbol (e.g., EURUSD)")
    timeframe: str = Field(description="Chart timeframe (e.g., 15m, 1h)")
    direction: Literal["LONG", "SHORT"] = Field(description="Trade direction")
    price_ctx: PriceCtx = Field(description="Price context data")
    atr: float = Field(description="Average True Range value")
    flags: Flags = Field(description="SMC confluence flags")