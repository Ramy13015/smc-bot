"""
Test automatique - Envoie des signaux de test sans interaction
"""
import requests
import json
import time

BOT_URL = "http://localhost:8000/tv"

# Signal de test réaliste
test_signal = {
    "event_id": f"BTCUSDT.P_{int(time.time() * 1000)}_LONG",
    "symbol": "BTCUSDT.P",
    "timeframe": "15",
    "direction": "LONG",
    "entry": 69500.00,
    "sl": 68875.00,
    "tp": 70500.00,
    "atr": 250.00,
    "poi_valid": True,
    "fvg_open": True,
    "ob_valid": True,
    "bos_confirm": True,
    "choch_confirm": True,
    "liq_swept": True,
    "imbalance_filled": True,
    "trend_aligned": True,
    "volume_confirm": True,
    "time_filter": True
}

print("="*60)
print("🧪 TEST AUTOMATIQUE - Signal vers Telegram")
print("="*60)

# Vérifier que le bot tourne
print("\n1️⃣ Vérification du bot...")
try:
    health = requests.get("http://localhost:8000/health", timeout=3).json()
    print(f"   ✅ Bot actif")
    print(f"   ✅ Telegram: {health['config']['telegram_configured']}")
    print(f"   ✅ Confluence: {health['config']['confluence_threshold']*100:.0f}%")
except:
    print("   ❌ Bot non démarré !")
    exit(1)

# Analyse du signal
print("\n2️⃣ Analyse du signal de test...")
flags = sum([test_signal[f] for f in ["poi_valid", "fvg_open", "ob_valid", "bos_confirm", 
             "choch_confirm", "liq_swept", "imbalance_filled", "trend_aligned", "volume_confirm", "time_filter"]])
confluence = (flags / 10.0) * 100

print(f"   📊 {test_signal['symbol']} {test_signal['direction']}")
print(f"   📊 Confluence: {confluence:.0f}% ({flags}/10 flags)")
print(f"   💰 Entry: {test_signal['entry']:.2f}")
print(f"   🛑 SL: {test_signal['sl']:.2f}")
print(f"   🎯 TP: {test_signal['tp']:.2f}")

# Envoi
print("\n3️⃣ Envoi vers le bot...")
try:
    response = requests.post(BOT_URL, json=test_signal, timeout=5)
    result = response.json()
    
    print(f"   Status: {response.status_code}")
    
    if result.get("sent"):
        print(f"\n   ✅✅✅ MESSAGE ENVOYÉ SUR TELEGRAM ! ✅✅✅")
        print(f"\n   📱 Vérifie ton Telegram maintenant !")
        print(f"\n   Les valeurs affichées sont:")
        print(f"   - Entry: {test_signal['entry']:.5f}")
        print(f"   - SL: {test_signal['sl']:.5f}")
        print(f"   - TP: {test_signal['tp']:.5f}")
        print(f"   - Confluence: {confluence:.1f}%")
        print(f"\n   Ces valeurs sont RÉELLES, pas inventées !")
    else:
        reason = result.get("reason", "unknown")
        print(f"\n   ⚠️ Signal NON envoyé: {reason}")
        if reason == "below_threshold":
            print(f"   Confluence {result.get('confluence'):.1f}% < 70%")
        
    print(f"\n   Réponse complète:")
    print(f"   {json.dumps(result, indent=2)}")
    
except Exception as e:
    print(f"\n   ❌ Erreur: {e}")

print("\n" + "="*60)
print("✅ Test terminé !")
print("="*60 + "\n")
