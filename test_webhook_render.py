"""
Test du webhook Render.com -> Telegram
Simule un signal SMC pour vérifier que tout fonctionne
"""
import requests
import json

# URL du bot sur Render.com
WEBHOOK_URL = "https://smc-gal.onrender.com/tv"

# Données de test - Signal LONG sur ETHUSDT.P avec 80% confluence (8/10 flags)
test_payload = {
    "event_id": "ETHUSDT.P_1730736100000_LONG",
    "symbol": "ETHUSDT.P",
    "timeframe": "15",
    "direction": "LONG",
    "entry": 3470.25,
    "sl": 3445.80,
    "tp": 3519.15,
    "atr": 9.78,
    "poi_valid": True,
    "fvg_open": True,  # Changé à True
    "ob_valid": True,
    "bos_confirm": True,
    "choch_confirm": False,
    "liq_swept": False,
    "imbalance_filled": True,
    "trend_aligned": True,
    "volume_confirm": True,
    "time_filter": True
}

print("=" * 60)
print("TEST WEBHOOK RENDER.COM → TELEGRAM")
print("=" * 60)
print(f"\n📡 Envoi vers: {WEBHOOK_URL}")
print(f"📊 Signal: {test_payload['direction']} sur {test_payload['symbol']}")
print(f"💰 Entry: {test_payload['entry']}")
print(f"🔴 SL: {test_payload['sl']}")
print(f"🟢 TP: {test_payload['tp']}")
print(f"\n⏳ Envoi en cours...")

try:
    response = requests.post(
        WEBHOOK_URL,
        json=test_payload,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    print(f"\n✅ Réponse reçue: HTTP {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Bot response: {json.dumps(result, indent=2)}")
        print("\n" + "=" * 60)
        print("✅ SUCCESS! Vérifiez votre Telegram maintenant!")
        print("=" * 60)
    else:
        print(f"❌ Erreur: {response.text}")
        
except requests.exceptions.Timeout:
    print("\n❌ TIMEOUT - Le bot Render.com ne répond pas (peut-être en veille)")
    print("💡 Render.com met les apps gratuites en veille après 15min d'inactivité")
    print("   Visitez https://smc-gal.onrender.com/health pour le réveiller")
    
except Exception as e:
    print(f"\n❌ ERREUR: {e}")
