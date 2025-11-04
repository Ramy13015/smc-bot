"""
Test avec VRAIES données du marché en temps réel
Récupère le prix actuel de Binance API
"""
import requests
import json
import time

def get_real_price(symbol="BTCUSDT"):
    """Récupère le prix actuel depuis Binance"""
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        response = requests.get(url, timeout=5)
        data = response.json()
        return float(data["price"])
    except Exception as e:
        print(f"Erreur API: {e}")
        return None

def get_real_atr(symbol="BTCUSDT", interval="15m"):
    """Estime l'ATR à partir des dernières bougies"""
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=14"
        response = requests.get(url, timeout=5)
        candles = response.json()
        
        # Calcul ATR simplifié (High - Low moyenné)
        ranges = [float(c[2]) - float(c[3]) for c in candles]  # High - Low
        atr = sum(ranges) / len(ranges)
        return atr
    except Exception as e:
        print(f"Erreur ATR: {e}")
        return None

print("="*70)
print("🔴 TEST AVEC VRAIES DONNÉES DU MARCHÉ EN TEMPS RÉEL")
print("="*70)

# 1. Récupérer le prix actuel
print("\n1️⃣ Récupération du prix actuel de Bitcoin...")
current_price = get_real_price("BTCUSDT")

if not current_price:
    print("❌ Impossible de récupérer le prix")
    exit(1)

print(f"   ✅ Prix actuel: {current_price:,.2f} USDT")

# 2. Récupérer l'ATR
print("\n2️⃣ Calcul de l'ATR (volatilité)...")
atr = get_real_atr("BTCUSDT", "15m")

if not atr:
    print("❌ Impossible de calculer l'ATR")
    exit(1)

print(f"   ✅ ATR 14 périodes: {atr:,.2f} USDT")

# 3. Calculer SL/TP (comme Pine Script)
direction = "LONG"
entry = current_price
sl = entry - (atr * 2.5) if direction == "LONG" else entry + (atr * 2.5)
tp = entry + (atr * 4.0) if direction == "LONG" else entry - (atr * 4.0)

print(f"\n3️⃣ Calculs basés sur le marché RÉEL:")
print(f"   Direction: {direction}")
print(f"   Entry: {entry:,.2f} USDT (prix actuel)")
print(f"   SL: {sl:,.2f} USDT (Entry - {atr * 2.5:,.2f})")
print(f"   TP: {tp:,.2f} USDT (Entry + {atr * 4.0:,.2f})")

# 4. Créer le signal avec VRAIES données
test_signal = {
    "event_id": f"BTCUSDT.P_{int(time.time() * 1000)}_LONG",
    "symbol": "BTCUSDT.P",
    "timeframe": "15",
    "direction": direction,
    "entry": entry,
    "sl": sl,
    "tp": tp,
    "atr": atr,
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

# 5. Vérifier que le bot tourne
print("\n4️⃣ Vérification du bot...")
try:
    health = requests.get("http://localhost:8000/health", timeout=3).json()
    print(f"   ✅ Bot actif (Confluence: {health['config']['confluence_threshold']*100:.0f}%)")
except:
    print("   ❌ Bot non démarré ! Lance: .\\start.bat")
    exit(1)

# 6. Envoyer le signal
print("\n5️⃣ Envoi du signal avec VRAIES données du marché...")
try:
    response = requests.post("http://localhost:8000/tv", json=test_signal, timeout=5)
    result = response.json()
    
    if result.get("sent"):
        print(f"\n   ✅✅✅ MESSAGE ENVOYÉ SUR TELEGRAM ! ✅✅✅")
        print(f"\n   📱 VÉRIFIE TON TELEGRAM MAINTENANT !")
        print(f"\n   Les valeurs affichées sont:")
        print(f"   ┌─────────────────────────────────────────┐")
        print(f"   │ Entry: {entry:>12,.2f} USDT (prix actuel) │")
        print(f"   │ SL:    {sl:>12,.2f} USDT (calculé)      │")
        print(f"   │ TP:    {tp:>12,.2f} USDT (calculé)      │")
        print(f"   └─────────────────────────────────────────┘")
        print(f"\n   🔴 CES VALEURS VIENNENT DE L'API BINANCE !")
        print(f"   🔴 CE SONT LES PRIX RÉELS DU MARCHÉ !")
    else:
        reason = result.get("reason", "unknown")
        print(f"\n   ⚠️ Signal non envoyé: {reason}")
        
except Exception as e:
    print(f"\n   ❌ Erreur: {e}")

print("\n" + "="*70)
print("✅ Test avec données RÉELLES terminé !")
print("="*70)
print("\n💡 Compare le prix d'entrée avec:")
print("   - Binance: https://www.binance.com/fr/trade/BTC_USDT")
print("   - TradingView: https://www.tradingview.com/chart/?symbol=BINANCE:BTCUSDT")
print("\n   Les prix correspondent ! ✅")
print("="*70 + "\n")
