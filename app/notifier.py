import httpx
from app.config import TG_BOT_TOKEN, TG_CHAT_ID


async def notify(msg: str) -> None:
    # si pas de token ou pas d'id, on ne fait rien
    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        return

    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": msg,
    }

    async with httpx.AsyncClient() as client:
        r = await client.post(url, data=payload, timeout=10.0)
        r.raise_for_status()
