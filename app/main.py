from fastapi import FastAPI, Request, HTTPException

from app.notifier import notify
from app.smc import evaluate_smc

app = FastAPI(title="SMC Bot Alerts")


@app.get("/health")
async def health():
    return {"ok": True}


@app.post("/tv")
async def receive_alert(req: Request):
    try:
        data = await req.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"invalid json: {e}")

    symbol = data.get("symbol", "Unknown")
    event = data.get("event", "unknown")
    side = data.get("side", "none")

    # scoring SMC
    smc_result = evaluate_smc(data)

    # message telegram
    if smc_result["send"]:
        msg = (
            "🔔 monbotfibo\n"
            f"Pair: {symbol}\n"
            f"Event: {event}\n"
            f"Side: {side.upper()}\n"
            f"Score: {smc_result['score']}/{smc_result['max']}\n"
            f"Reasons: {', '.join(smc_result['reasons']) or '—'}"
        )
        await notify(msg)

    return {
        "ok": True,
        "received": data,
        "smc": smc_result,
    }
