# Fichier: app/config.py
import os
# Il n'y a pas besoin d'importer conf ou load_dotenv,
# car Render gère les variables d'environnement.

# Utilisation de os.environ.get() pour récupérer les variables
TELEGRAM_BOT_TOKEN = os.environ.get("TEL_BOT_TOKEN") 
TELEGRAM_CHAT_ID = os.environ.get("TEL_CHAT_ID")
# Note : Les noms des variables doivent correspondre exactement à ceux que vous avez sur Render (TEL_BOT_TOKEN, TEL_CHAT_ID).

# Suppression de toutes les autres lignes (conf.options, FAST=uvicorn.run, etc.)
