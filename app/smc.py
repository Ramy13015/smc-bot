from typing import Dict, Any, List

# critères qu'on attend depuis TradingView
CRITERIA: List[str] = [
    "bos_choch",           # BOS / CHoCH validé
    "poi_valid",           # POI / OB propre
    "idm_transfer",        # IDM + transfert
    "orderflow_unmitigated",  # zone non mitigée
    "fibo_confluence",     # zone 50% / golden
    "smt_filter",          # filtre SMT ok
    "lcf_ok",              # low-conflict filter
]


def evaluate_smc(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    TradingView nous envoie un JSON.
    On regarde combien de critères sont à True.
    À partir de 5/7 on envoie sur Telegram.
    """
    score = 0
    reasons: List[str] = []

    for key in CRITERIA:
        if bool(data.get(key, False)):
            score += 1
            reasons.append(key)

    max_score = len(CRITERIA)
    send = score >= 5  # seuil

    return {
        "score": score,
        "max": max_score,
        "reasons": reasons,
        "send": send,
    }
