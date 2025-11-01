# Fichier: app/config.py

import os

# Récupère les variables d'environnement de Render
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Ligne FAST = uvicorn.run(...) DÉFINITIVEMENT SUPPRIMÉE
