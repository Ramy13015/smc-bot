"""
SMC (Smart Money Concepts) scoring and risk management functions
"""
from typing import Tuple, List
from app.models import Flags, TVPayload


# SMC Flag Weights for Confluence Scoring
WEIGHTS = {
    "poi_valid": 0.25,      # Critical: Point of Interest
    "fvg_open": 0.15,       # Critical: Fair Value Gap
    "ob_valid": 0.12,
    "bos_confirm": 0.10,
    "choch_confirm": 0.08,
    "liq_swept": 0.08,
    "imbalance_filled": 0.07,
    "trend_aligned": 0.06,
    "volume_confirm": 0.05,
    "time_filter": 0.04
}

# Critical flags that must be present
CRITICAL_FLAGS = ["poi_valid", "fvg_open"]


def calculate_confluence_score(flags: Flags) -> float:
    """
    Calculate SMC confluence score based on weighted flags
    
    Args:
        flags: SMC flags object
        
    Returns:
        Float score between 0.0 and 1.0
    """
    total_score = 0.0
    
    for flag_name, weight in WEIGHTS.items():
        if hasattr(flags, flag_name) and getattr(flags, flag_name):
            total_score += weight
    
    return total_score


def validate_critical_flags(flags: Flags) -> Tuple[bool, str]:
    """
    Validate that critical SMC flags are present
    
    Args:
        flags: SMC flags object
        
    Returns:
        Tuple of (is_valid, reason)
    """
    missing_flags = []
    
    for critical_flag in CRITICAL_FLAGS:
        if not hasattr(flags, critical_flag) or not getattr(flags, critical_flag):
            missing_flags.append(critical_flag)
    
    if missing_flags:
        return False, f"Missing critical flags: {', '.join(missing_flags)}"
    
    return True, "All critical flags present"


def calculate_risk_parameters(
    payload: TVPayload,
    base_equity: float,
    risk_pct: float,
    atr_sl_mult: float,
    atr_tp_mult: float
) -> Tuple[float, float, float, float]:
    """
    Calculate entry, stop loss, take profit, and position size
    
    Args:
        payload: TradingView payload
        base_equity: Base trading capital
        risk_pct: Risk percentage per trade
        atr_sl_mult: ATR multiplier for stop loss
        atr_tp_mult: ATR multiplier for take profit
        
    Returns:
        Tuple of (entry, stop_loss, take_profit, position_size)
    """
    entry = payload.price_ctx.entry
    atr = payload.atr
    direction = payload.direction
    
    # Calculate stop loss and take profit based on ATR
    if direction == "LONG":
        stop_loss = entry - (atr * atr_sl_mult)
        take_profit = entry + (atr * atr_tp_mult)
    else:  # SHORT
        stop_loss = entry + (atr * atr_sl_mult)
        take_profit = entry - (atr * atr_tp_mult)
    
    # Calculate position size based on risk
    risk_amount = base_equity * risk_pct
    price_distance = abs(entry - stop_loss)
    position_size = risk_amount / price_distance if price_distance > 0 else 0
    
    return entry, stop_loss, take_profit, position_size


def calculate_rr_ratio(entry: float, stop_loss: float, take_profit: float) -> float:
    """
    Calculate Risk:Reward ratio
    
    Args:
        entry: Entry price
        stop_loss: Stop loss price
        take_profit: Take profit price
        
    Returns:
        Risk:Reward ratio
    """
    risk = abs(entry - stop_loss)
    reward = abs(take_profit - entry)
    
    return reward / risk if risk > 0 else 0


def get_active_flags(flags: Flags) -> List[str]:
    """
    Get list of active (True) flags
    
    Args:
        flags: SMC flags object
        
    Returns:
        List of active flag names
    """
    active_flags = []
    
    for flag_name in WEIGHTS.keys():
        if hasattr(flags, flag_name) and getattr(flags, flag_name):
            active_flags.append(flag_name.replace('_', ' ').title())
    
    return active_flags