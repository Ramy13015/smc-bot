"""
smc_ai.py - GROK + DEEPSEEK IA ENGINE
Valide les signaux SMC + calcule SL/TP + sentiment
"""
import requests
import json
from typing import Dict, Optional

# === CONFIG ===
GROK_API_KEY = "YOUR_GROK_API_KEY"
DEEPSEEK_API_KEY = "YOUR_DEEPSEEK_API_KEY"

GROK_URL = "https://api.x.ai/v1/chat/completions"
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

HEADERS_GROK = {
    "Authorization": f"Bearer {GROK_API_KEY}",
    "Content-Type": "application/json"
}

HEADERS_DEEPSEEK = {
    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
    "Content-Type": "application/json"
}

def ask_grok(signal: Dict) -> Optional[Dict]:
    """Demande à GROK si le signal est valide"""
    prompt = f"""
    Tu es un expert SMC. Analyse ce signal :
    {json.dumps(signal, indent=2)}
    
    Réponds UNIQUEMENT en JSON :
    {{
        "decision": "BUY" | "SELL" | "REJECT",
        "confidence": 0-100,
        "reason": "explication courte"
    }}
    """
    
    try:
        response = requests.post(
            GROK_URL,
            headers=HEADERS_GROK,
            json={
                "model": "grok-beta",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1
            },
            timeout=10
        )
        return response.json()["choices"][0]["message"]["content"]
    except:
        return None

def ask_deepseek(signal: Dict) -> Optional[Dict]:
    """Demande à DEEPSEEK : SL/TP + sentiment"""
    prompt = f"""
    Calcule pour ce signal SMC :
    {json.dumps(signal, indent=2)}
    
    Réponds UNIQUEMENT en JSON :
    {{
        "sl": float,
        "tp": float,
        "sentiment": "bullish" | "bearish" | "neutral",
        "risk_reward": float
    }}
    """
    
    try:
        response = requests.post(
            DEEPSEEK_URL,
            headers=HEADERS_DEEPSEEK,
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.0
            },
            timeout=10
        )
        return response.json()["choices"][0]["message"]["content"]
    except:
        return None

def process_with_ai(signal: Dict) -> Optional[Dict]:
    """Pipeline GROK + DEEPSEEK"""
    # 1. GROK valide
    grok = ask_grok(signal)
    if not grok or grok.get("decision") == "REJECT":
        return None
    
    # 2. DEEPSEEK calcule
    deepseek = ask_deepseek(signal)
    if not deepseek:
        return None
    
    return {
        "symbol": signal["symbol"],
        "direction": grok["decision"],
        "entry": signal["price_ctx"]["entry"],
        "sl": deepseek["sl"],
        "tp": deepseek["tp"],
        "risk_reward": deepseek["risk_reward"],
        "confidence": grok["confidence"],
        "sentiment": deepseek["sentiment"]
    }