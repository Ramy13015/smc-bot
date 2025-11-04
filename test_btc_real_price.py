"""
Test avec le prix BTC RÉEL pour vérifier que Telegram reçoit les bonnes valeurs
"""
import requests
import json
from datetime import datetime

# Récupérer le prix BTC actuel
print("⏳ Récupération du prix BTC réel depuis Binance...")
btc_data = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT').json()
btc_price = float(btc_data['price'])
print(f"✅ Prix BTC actuel: ${btc_price:,.2f}")

# Simuler un ATR réaliste (environ 0.5% du prix)
atr = btc_price * 0.005
entry_price = btc_price
sl_price = entry_price - (atr * 2.5)  # LONG stop loss
tp_price = entry_price + (atr * 4.0)  # LONG take profit

print(f"\n📊 Signal LONG simulé:")
print(f"   Entry: ${entry_price:,.2f}")
print(f"   SL:    ${sl_price:,.2f} (-{((entry_price - sl_price) / entry_price * 100):.2f}%)")
print(f"   TP:    ${tp_price:,.2f} (+{((tp_price - entry_price) / entry_price * 100):.2f}%)")
print(f"   ATR:   ${atr:,.2f}")

# Webhook URL
WEBHOOK_URL = "https://smc-gal.onrender.com/tv"

# Payload avec prix RÉEL
test_payload = {
    "event_id": f"BTCUSDT.P_{int(datetime.now().timestamp() * 1000)}_LONG",
    "symbol": "BTCUSDT.P",
    "timeframe": "15",
    "direction": "LONG",
    "entry": round(entry_price, 2),
    "sl": round(sl_price, 2),
    "tp": round(tp_price, 2),
    "atr": round(atr, 2),
    "poi_valid": True,
    "fvg_open": True,
    "ob_valid": True,
    "bos_confirm": True,
    "choch_confirm": False,
    "liq_swept": False,
    "imbalance_filled": True,
    "trend_aligned": True,
    "volume_confirm": True,
    "time_filter": True
}

print("\n" + "=" * 60)
print("📡 ENVOI DU SIGNAL VERS TELEGRAM")
print("=" * 60)
print(f"URL: {WEBHOOK_URL}")
print(f"Confluence: 80% (8/10 flags)")
print("\n⏳ Envoi en cours...")

try:
    response = requests.post(
        WEBHOOK_URL,
        json=test_payload,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    print(f"\n✅ Réponse: HTTP {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n📱 Message envoyé sur Telegram !")
        print(f"Bot response: {json.dumps(result, indent=2)}")
        print("\n" + "=" * 60)
        print("✅ VÉRIFIEZ VOTRE TELEGRAM MAINTENANT!")
        print("=" * 60)
        print(f"\n🔍 Le prix dans Telegram devrait être:")
        print(f"   Entry: ${entry_price:,.2f}")
        print(f"   SL:    ${sl_price:,.2f}")
        print(f"   TP:    ${tp_price:,.2f}")
        print(f"\n⚠️  Comparez ces valeurs avec le message Telegram!")
    else:
        print(f"❌ Erreur: {response.text}")
        
except Exception as e:
    print(f"\n❌ ERREUR: {e}")
