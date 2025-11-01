# Fichier: app/main.py

from fastapi import FastAPI, Request, HTTPException
# CORRECTION 1: Utilisez l'importation complète du module
from app.notifier import notify
from app.smc import evaluate_smc
# CORRECTION 2: Importez les variables de configuration (nécessaires pour notify)
from app.config import TELEGRAM_CHAT_ID

app = FastAPI(title="SMC Bot Alerts")

# --- ROUTES DE TEST ET HEALTH CHECK ---
@app.get("/")
def root():
    # C'est la bonne route pour vérifier le statut du service
    return {"status": "running", "info": "SMC bot is online"}

@app.get("/health")
def health():
    return {"ok": True}

# --- ROUTE WEBHOOK /tv ---
@app.post("/tv")
async def receive_alert(req: Request):
    try:
        data = await req.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON format: {e}")
    
    symbol = data.get("symbol", "unknown")
    event = data.get("event", "unknown")
    side = data.get("side", "none")
    price = data.get("price", None)
    timeframe = data.get("timeframe", None)
    
    # scoring SMC
    smc_result = evaluate_smc(data)
    
    if smc_result["send"]:
        msg_lines = [
            "📈 **monbotfibo**",
            f"**Pair:** {symbol}",
            f"**Event:** {event}",
            f"**Side:** {side.upper()}",
            f"**Score:** {smc_result['score']}/{smc_result['max']}",
        ]
        if price:
            msg_lines.append(f"Price: {price}")
        if timeframe:
            msg_lines.append(f"TF: {timeframe}")
        if smc_result["reasons"]:
            msg_lines.append("Confluences: " + ", ".join(smc_result["reasons"]))
            
        msg = "\n".join(msg_lines)
        
        # CORRECTION 3: Utilisez la variable TELEGRAM_CHAT_ID importée
        await notify(msg, TELEGRAM_CHAT_ID)
    
    return {
        "ok": True,
        "received": data,
        "smc": smc_result,
    }
