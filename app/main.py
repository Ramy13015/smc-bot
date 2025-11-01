from fastapi import FastAPI, Request, HTTPException
from app.notifier import notify
from app.smc import evaluate_smc

app = FastAPI(title="SMC Bot Alerts")

# --- ROUTES DE TEST ---
@app.get("/")
def root():
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
        raise HTTPException(status_code=400, detail=f"invalid json: {e}")

    symbol = data.get("symbol", "unknown")
    event = data.get("event", "unknown")
    side = data.get("side", "none")
    price = data.get("price", None)
    timeframe = data.get("timeframe", None)

    # scoring SMC
    smc_result = evaluate_smc(data)

    if smc_result["send"]:
        msg_lines = [
            "📈 monbotfibo",
            f"Pair: {symbol}",
            f"Event: {event}",
            f"Side: {side.upper()}",
            f"Score: {smc_result['score']}/{smc_result['max']}",
        ]
        if price:
            msg_lines.append(f"Price: {price}")
        if timeframe:
            msg_lines.append(f"TF: {timeframe}")
        if smc_result["reasons"]:
            msg_lines.append("Confluences: " + ", ".join(smc_result["reasons"]))

        msg = "\n".join(msg_lines)
        await notify(msg)

    return {
        "ok": True,
        "received": data,
        "smc": smc_result,
    }
