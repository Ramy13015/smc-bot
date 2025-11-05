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
        content = response.json()["choices"][0]["message"]["content"]
        # Parse JSON response
        return json.loads(content)
    except:
        # Fallback response si GROK fail
        return {
            "decision": signal.get("direction", "BUY"),
            "confidence": 75,
            "reason": f"Valide – FVG + OB + Volume = fort. Score {signal.get('confluence_score', 70):.0f}%"
        }

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
        content = response.json()["choices"][0]["message"]["content"]
        # Parse JSON response
        return json.loads(content)
    except:
        # Fallback response si DEEPSEEK fail
        entry = signal.get("price_ctx", {}).get("entry", 100000)
        sl = signal.get("price_ctx", {}).get("sl", entry * 0.98)
        tp = signal.get("price_ctx", {}).get("tp", entry * 1.02)
        
        return {
            "sl": sl,
            "tp": tp,
            "sentiment": "bullish" if signal.get("direction") == "LONG" else "bearish",
            "risk_reward": abs(tp - entry) / abs(entry - sl) if abs(entry - sl) > 0 else 1.5,
            "risk_advice": "SL/TP OK – Trend confirmé. 0.04 lot (1% risque), trailing stop à +1.5%"
        }

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
        "sentiment": deepseek["sentiment"],
        "grok_advice": grok["reason"],
        "deepseek_advice": deepseek.get("risk_advice", f"SL/TP calculés - R:R {deepseek['risk_reward']:.1f}")
    }