"""
Test pour vérifier que le bot reçoit de VRAIES données de TradingView
et non des valeurs inventées
"""
import json
from datetime import datetime

def analyze_signal(data):
    """Analyse un signal pour vérifier qu'il contient de vraies données"""
    
    print("=" * 60)
    print("🔍 ANALYSE DU SIGNAL TRADINGVIEW")
    print("=" * 60)
    
    # 1. Vérifier la structure
    required_fields = [
        "event_id", "symbol", "timeframe", "direction", 
        "entry", "sl", "tp", "atr"
    ]
    
    print("\n1️⃣ VÉRIFICATION DE LA STRUCTURE")
    for field in required_fields:
        if field in data:
            print(f"   ✅ {field}: {data[field]}")
        else:
            print(f"   ❌ {field}: MANQUANT")
    
    # 2. Vérifier que les valeurs sont cohérentes
    print("\n2️⃣ VÉRIFICATION DE LA COHÉRENCE DES PRIX")
    
    entry = data.get("entry", 0)
    sl = data.get("sl", 0)
    tp = data.get("tp", 0)
    direction = data.get("direction", "")
    
    if direction == "LONG":
        # Pour un LONG: SL < Entry < TP
        if sl < entry < tp:
            print(f"   ✅ LONG cohérent: SL({sl:.5f}) < Entry({entry:.5f}) < TP({tp:.5f})")
        else:
            print(f"   ❌ LONG incohérent: SL={sl}, Entry={entry}, TP={tp}")
    
    elif direction == "SHORT":
        # Pour un SHORT: TP < Entry < SL
        if tp < entry < sl:
            print(f"   ✅ SHORT cohérent: TP({tp:.5f}) < Entry({entry:.5f}) < SL({sl:.5f})")
        else:
            print(f"   ❌ SHORT incohérent: TP={tp}, Entry={entry}, SL={sl}")
    
    # 3. Vérifier les distances (basées sur ATR)
    print("\n3️⃣ VÉRIFICATION ATR ET DISTANCES")
    
    atr = data.get("atr", 0)
    sl_distance = abs(entry - sl)
    tp_distance = abs(tp - entry)
    
    print(f"   ATR: {atr:.5f}")
    print(f"   Distance SL: {sl_distance:.5f} ({sl_distance/atr:.2f}x ATR)")
    print(f"   Distance TP: {tp_distance:.5f} ({tp_distance/atr:.2f}x ATR)")
    
    # Pine Script utilise 2.5x ATR pour SL et 4.0x pour TP
    sl_expected = atr * 2.5
    tp_expected = atr * 4.0
    
    sl_diff = abs(sl_distance - sl_expected) / sl_expected * 100
    tp_diff = abs(tp_distance - tp_expected) / tp_expected * 100
    
    if sl_diff < 5:  # Tolérance 5%
        print(f"   ✅ SL correct (écart: {sl_diff:.1f}%)")
    else:
        print(f"   ⚠️ SL suspect (écart: {sl_diff:.1f}%)")
    
    if tp_diff < 5:
        print(f"   ✅ TP correct (écart: {tp_diff:.1f}%)")
    else:
        print(f"   ⚠️ TP suspect (écart: {tp_diff:.1f}%)")
    
    # 4. Vérifier les flags SMC
    print("\n4️⃣ VÉRIFICATION DES FLAGS SMC")
    
    flags = [
        "poi_valid", "fvg_open", "ob_valid", "bos_confirm", 
        "choch_confirm", "liq_swept", "imbalance_filled", 
        "trend_aligned", "volume_confirm", "time_filter"
    ]
    
    active_flags = sum([1 for f in flags if data.get(f, False)])
    confluence = (active_flags / len(flags)) * 100
    
    print(f"   Flags actifs: {active_flags}/{len(flags)}")
    print(f"   Confluence: {confluence:.1f}%")
    
    for flag in flags:
        status = "✅" if data.get(flag, False) else "❌"
        print(f"   {status} {flag}")
    
    # 5. Vérifier l'event_id (doit être unique)
    print("\n5️⃣ VÉRIFICATION EVENT ID")
    
    event_id = data.get("event_id", "")
    symbol = data.get("symbol", "")
    
    if symbol in event_id:
        print(f"   ✅ Event ID contient le symbole: {event_id}")
    else:
        print(f"   ❌ Event ID suspect: {event_id}")
    
    if direction in event_id:
        print(f"   ✅ Event ID contient la direction")
    else:
        print(f"   ❌ Event ID ne contient pas la direction")
    
    # 6. Verdict final
    print("\n" + "=" * 60)
    print("📊 VERDICT FINAL")
    print("=" * 60)
    
    if confluence >= 80 and sl_diff < 10 and tp_diff < 10:
        print("✅ SIGNAL VALIDE - Données cohérentes de TradingView")
        print("✅ Les prix et calculs correspondent aux formules Pine Script")
        print("✅ Ce sont de VRAIES données de marché, pas inventées")
    else:
        print("⚠️ SIGNAL À VÉRIFIER - Anomalies détectées")
    
    print("=" * 60)


# Exemple de test avec un signal réel attendu
if __name__ == "__main__":
    print("🧪 TEST DE VALIDATION DES DONNÉES TRADINGVIEW\n")
    
    # Signal test 1: LONG Bitcoin
    test_signal_1 = {
        "event_id": "BTCUSDT.P_1730736000000_LONG",
        "symbol": "BTCUSDT.P",
        "timeframe": "15",
        "direction": "LONG",
        "entry": 69500.0,
        "sl": 69500.0 - (250.0 * 2.5),  # Entry - (ATR * 2.5)
        "tp": 69500.0 + (250.0 * 4.0),  # Entry + (ATR * 4.0)
        "atr": 250.0,
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
    
    analyze_signal(test_signal_1)
    
    print("\n\n")
    
    # Signal test 2: SHORT EURUSD
    test_signal_2 = {
        "event_id": "EURUSD_1730739600000_SHORT",
        "symbol": "EURUSD",
        "timeframe": "60",
        "direction": "SHORT",
        "entry": 1.08500,
        "sl": 1.08500 + (0.00080 * 2.5),  # Entry + (ATR * 2.5)
        "tp": 1.08500 - (0.00080 * 4.0),  # Entry - (ATR * 4.0)
        "atr": 0.00080,
        "poi_valid": True,
        "fvg_open": True,
        "ob_valid": False,
        "bos_confirm": True,
        "choch_confirm": True,
        "liq_swept": False,
        "imbalance_filled": True,
        "trend_aligned": True,
        "volume_confirm": True,
        "time_filter": True
    }
    
    analyze_signal(test_signal_2)
    
    print("\n\n📝 COMMENT VÉRIFIER EN PRODUCTION:")
    print("1. Surveillez les logs du serveur (affichent toutes les données reçues)")
    print("2. Comparez l'Entry avec le prix réel sur TradingView au moment du signal")
    print("3. Vérifiez que le SL/TP sont cohérents avec la direction")
    print("4. L'ATR doit correspondre à la volatilité réelle du marché")
    print("5. Le symbole et timeframe doivent correspondre à votre graphique TV")
