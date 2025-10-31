from fastapi import FastAPI, Request
from app.notifier import notify, fmt

app = FastAPI(title="SMC Bot Alerts")


@app.post("/tv")
async def receive_alert(req: Request):
    data = await req.json()
    symbol = data.get("symbol", "Unknown")
    event = data.get("event", "none")
    side = data.get("side", "none")
    msg = fmt(symbol, event, side)
    await notify(msg)
    return {"ok": True, "received": data}


@app.get("/health")
async def health():
    return {"ok": True}
