# Fichier: app/notifier.py

import httpx
# CORRECTION D'IMPORTATION : Importation relative pour les déploiements sur Render
from app.config import TELEGRAM_BOT_TOKEN 

async def notify(message: str, chat_id: str):
    """
    Envoie une notification formatée via l'API Telegram.
    
    :param message: Le texte à envoyer.
    :param chat_id: L'ID du chat/canal Telegram.
    """
    
    if not TELEGRAM_BOT_TOKEN:
        print("Erreur: TELEGRAM_BOT_TOKEN n'est pas configuré.")
        return {"error": "Token Telegram manquant", "sent": False}
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown", # Permet d'utiliser **gras**, *italique*, etc.
        "disable_notification": False # Laisse la notification normale
    }

    try:
        # Utilisation de httpx.AsyncClient pour une requête non bloquante (asynchrone)
        async with httpx.AsyncClient() as client:
            # Timeout de 5 secondes pour éviter de bloquer l'API
            response = await client.post(url, data=data, timeout=5)
            # Vérifie si le code de statut est une erreur (4xx ou 5xx) et lève une exception si c'est le cas
            response.raise_for_status() 
            
            print(f"Notification Telegram envoyée. Statut: {response.status_code}")
            return response.json()
            
    except httpx.RequestError as e:
        # Erreur lors de l'établissement de la connexion (DNS, timeout initial, etc.)
        print(f"Erreur de requête HTTP lors de l'envoi Telegram: {e}")
        return {"error": str(e), "sent": False}
        
    except httpx.HTTPStatusError as e:
        # Erreur retournée par l'API Telegram (e.g., chat_id incorrect, token invalide)
        error_detail = e.response.text
        print(f"Erreur de statut HTTP Telegram: {error_detail}")
        return {"error": error_detail, "sent": False}
