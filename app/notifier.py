# Fichier: app/notifier.py

import httpx
# CORRECTION ESSENTIELLE : Importation correcte du package
from app.config import TELEGRAM_BOT_TOKEN 

async def notify(message: str, chat_id: str):
    """
    Envoie une notification formatée via l'API Telegram.
    """
    
    if not TELEGRAM_BOT_TOKEN:
        print("Erreur: TELEGRAM_BOT_TOKEN n'est pas configuré.")
        return {"error": "Token Telegram manquant", "sent": False}
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown", 
        "disable_notification": False 
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data, timeout=5)
            response.raise_for_status() 
            
            print(f"Notification Telegram envoyée. Statut: {response.status_code}")
            return response.json()
            
    except httpx.RequestError as e:
        print(f"Erreur de requête HTTP lors de l'envoi Telegram: {e}")
        return {"error": str(e), "sent": False}
        
    except httpx.HTTPStatusError as e:
        error_detail = e.response.text
        print(f"Erreur de statut HTTP Telegram: {error_detail}")
        return {"error": error_detail, "sent": False}
