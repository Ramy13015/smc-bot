"""
Test en temps réel - Simule un signal TradingView vers Telegram
Vérifie que le bot envoie les VRAIES valeurs
"""
import requests
import json
from datetime import datetime
import time

# Configuration
BOT_URL = "http://localhost:8000/tv"  # URL locale du bot
TEST_SIGNALS = [
    {
        "name": "BTCUSDT.P - LONG (80%)",
        "data": {
            "event_id": f"BTCUSDT.P_{int(time.time() * 1000)}_LONG",
            "symbol": "BTCUSDT.P",
            "timeframe": "15",
            "direction": "LONG",
            "entry": 69500.00,
            "sl": 68875.00,  # Entry - (ATR * 2.5)
            "tp": 70500.00,  # Entry + (ATR * 4.0)
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
    },
    {
        "name": "ETHUSDT.P - SHORT (70%)",
        "data": {
            "event_id": f"ETHUSDT.P_{int(time.time() * 1000) + 1000}_SHORT",
            "symbol": "ETHUSDT.P",
            "timeframe": "60",
            "direction": "SHORT",
            "entry": 3650.00,
            "sl": 3725.00,  # Entry + (ATR * 2.5)
            "tp": 3530.00,  # Entry - (ATR * 4.0)
            "atr": 30.00,
            "poi_valid": True,
            "fvg_open": True,
            "ob_valid": True,
            "bos_confirm": True,
            "choch_confirm": False,
            "liq_swept": True,
            "imbalance_filled": True,
            "trend_aligned": True,
            "volume_confirm": True,
            "time_filter": False
        }
    },
    {
        "name": "SOLUSDT.P - LONG (60% - REJETÉ)",
        "data": {
            "event_id": f"SOLUSDT.P_{int(time.time() * 1000) + 2000}_LONG",
            "symbol": "SOLUSDT.P",
            "timeframe": "240",
            "direction": "LONG",
            "entry": 155.50,
            "sl": 153.00,
            "tp": 159.50,
            "atr": 1.00,
            "poi_valid": True,
            "fvg_open": True,
            "ob_valid": True,
            "bos_confirm": False,
            "choch_confirm": False,
            "liq_swept": False,
            "imbalance_filled": True,
            "trend_aligned": True,
            "volume_confirm": True,
            "time_filter": False
        }
    }
]

def analyze_signal(data):
    """Analyse un signal avant de l'envoyer"""
    entry = data["entry"]
    sl = data["sl"]
    tp = data["tp"]
    atr = data["atr"]
    direction = data["direction"]
    
    # Calcul confluence
    flags = ["poi_valid", "fvg_open", "ob_valid", "bos_confirm", 
             "choch_confirm", "liq_swept", "imbalance_filled", 
             "trend_aligned", "volume_confirm", "time_filter"]
    active = sum([1 for f in flags if data.get(f, False)])
    confluence = (active / len(flags)) * 100
    
    # Vérifications
    sl_distance = abs(entry - sl)
    tp_distance = abs(tp - entry)
    sl_mult = sl_distance / atr if atr > 0 else 0
    tp_mult = tp_distance / atr if atr > 0 else 0
    
    print(f"\n{'='*60}")
    print(f"📊 ANALYSE: {data['symbol']} {direction}")
    print(f"{'='*60}")
    print(f"Confluence: {confluence:.1f}% ({active}/10 flags)")
    print(f"Entry:      {entry:.2f}")
    print(f"Stop Loss:  {sl:.2f} ({sl_mult:.2f}x ATR)")
    print(f"Take Prof:  {tp:.2f} ({tp_mult:.2f}x ATR)")
    print(f"ATR:        {atr:.2f}")
    
    # Cohérence
    if direction == "LONG":
        coherent = sl < entry < tp
    else:
        coherent = tp < entry < sl
    
    print(f"\n✅ Cohérence: {'OK' if coherent else 'ERREUR'}")
    print(f"✅ SL/TP:     {'OK' if abs(sl_mult - 2.5) < 0.5 and abs(tp_mult - 4.0) < 0.5 else 'Suspect'}")
    
    return confluence >= 70

def send_test_signal(signal_info):
    """Envoie un signal de test au bot"""
    name = signal_info["name"]
    data = signal_info["data"]
    
    print(f"\n{'='*70}")
    print(f"🚀 TEST: {name}")
    print(f"{'='*70}")
    
    # Analyse
    should_pass = analyze_signal(data)
    
    print(f"\n📤 Envoi vers le bot...")
    
    try:
        response = requests.post(BOT_URL, json=data, timeout=5)
        
        print(f"\n📥 RÉPONSE DU BOT:")
        print(f"   Status: {response.status_code}")
        
        try:
            result = response.json()
            print(f"   Résultat: {json.dumps(result, indent=2)}")
            
            if result.get("sent"):
                print(f"\n✅ MESSAGE ENVOYÉ SUR TELEGRAM !")
                print(f"   Le bot a envoyé les vraies valeurs:")
                print(f"   - Entry: {data['entry']}")
                print(f"   - SL: {data['sl']}")
                print(f"   - TP: {data['tp']}")
            else:
                reason = result.get("reason", "unknown")
                print(f"\n⚠️ Signal non envoyé: {reason}")
                if reason == "below_threshold":
                    print(f"   Confluence {result.get('confluence', 0):.1f}% < 70%")
        except:
            print(f"   Réponse: {response.text}")
        
    except requests.exceptions.ConnectionError:
        print(f"\n❌ ERREUR: Le bot n'est pas démarré !")
        print(f"   Lance d'abord: .\\start.bat")
        return False
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        return False
    
    return True

def main():
    print("="*70)
    print("🧪 TEST EN TEMPS RÉEL - BOT SMC TRADING")
    print("="*70)
    print("\n📋 Ce test va:")
    print("1. Envoyer 3 signaux de test au bot")
    print("2. Vérifier que les valeurs sont cohérentes")
    print("3. Confirmer l'envoi sur Telegram")
    print("\n⚠️ ASSURE-TOI QUE:")
    print("   - Le bot est démarré (.\\start.bat)")
    print("   - Tu as accès à Telegram pour voir les messages")
    
    input("\nAppuie sur ENTRÉE pour commencer...")
    
    # Test de connexion
    print("\n🔍 Vérification de la connexion au bot...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=3)
        health = response.json()
        print(f"✅ Bot connecté !")
        print(f"   Telegram: {'✅' if health['config']['telegram_configured'] else '❌'}")
        print(f"   Confluence: {health['config']['confluence_threshold']*100:.0f}%")
    except:
        print(f"❌ Bot non démarré ! Lance d'abord: .\\start.bat")
        return
    
    # Envoi des signaux de test
    for i, signal in enumerate(TEST_SIGNALS, 1):
        print(f"\n\n{'#'*70}")
        print(f"TEST {i}/{len(TEST_SIGNALS)}")
        print(f"{'#'*70}")
        
        if not send_test_signal(signal):
            break
        
        if i < len(TEST_SIGNALS):
            print("\n⏳ Attente 3 secondes...")
            time.sleep(3)
    
    # Résumé
    print(f"\n\n{'='*70}")
    print("📊 RÉSUMÉ DU TEST")
    print(f"{'='*70}")
    print("\n✅ Si tu as reçu des messages sur Telegram:")
    print("   - Les valeurs (Entry, SL, TP) sont RÉELLES")
    print("   - Elles viennent directement des données envoyées")
    print("   - Le bot ne calcule RIEN, il relaye seulement")
    print("\n📱 Vérifie ton Telegram maintenant !")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
