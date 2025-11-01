from typing import Dict, Any, List

# critères attendus depuis TradingView / Pine
CRITERIA: List[str] = [
    "bos_or_choch",     # EP2/EP3
    "poi_valid",        # OB / POI propre
    "idm_transfer",     # IDM ou transfert
    "of_not_mitigated", # order flow non mitigé
    "fibo_zone",        # 50-61.8
    "smt_filter",       # filtre SMT OK
    "lcf_ok",           # low-conflict filter
]

def evaluate_smc(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    data = JSON reçu de TradingView
    ex:
    {
      "symbol": "BTCUSDT",
      "event": "signal_tv",
      "side": "long",
      "bos_or_choch": true,
      "poi_valid": true,
      "idm_transfer": false,
      "of_not_mitigated": true,
      ...
    }
    """

    score = 0
    reasons: List[str] = []

    for key in CRITERIA:
        if bool(data.get(key, False)):
            score += 1
            reasons.append(key)

    max_score = len(CRITERIA)

    # règle simple : on envoie si au moins 5 critères sur 7 sont OK
    send = score >= 5

    return {
        "score": score,
        "max": max_score,
        "reasons": reasons,
        "send": send,
    }
