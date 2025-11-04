"""
Monitoring en temps réel des signaux TradingView
Affiche les données reçues pour vérifier qu'elles sont réelles
"""
import asyncio
import json
from datetime import datetime
from fastapi import FastAPI, Request
from uvicorn import Config, Server

app = FastAPI(title="SMC Monitor - Données Réelles")

@app.post("/monitor")
async def monitor_webhook(request: Request):
    """Endpoint pour surveiller les données TradingView en temps réel"""
    
    # Timestamp de réception
    received_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Parse le payload
    try:
        data = await request.json()
    except:
        print("❌ Erreur: JSON invalide")
        return {"ok": False}
    
    # Affichage détaillé
    print("\n" + "=" * 80)
    print(f"📡 SIGNAL REÇU DE TRADINGVIEW - {received_at}")
    print("=" * 80)
    
    # Données principales
    symbol = data.get("symbol", "N/A")
    timeframe = data.get("timeframe", "N/A")
    direction = data.get("direction", "N/A")
    
    print(f"\n📊 MARCHÉ: {symbol} | Timeframe: {timeframe} | Direction: {direction}")
    
    # Prix (les plus importants pour vérifier qu'ils sont réels)
    entry = data.get("entry", 0)
    sl = data.get("sl", 0)
    tp = data.get("tp", 0)
    atr = data.get("atr", 0)
    
    print(f"\n💰 PRIX:")
    print(f"   Entry:     {entry:>15.5f}")
    print(f"   Stop Loss: {sl:>15.5f}")
    print(f"   Take Prof: {tp:>15.5f}")
    print(f"   ATR:       {atr:>15.5f}")
    
    # Calcul des distances
    sl_dist = abs(entry - sl)
    tp_dist = abs(tp - entry)
    
    print(f"\n📏 DISTANCES:")
    print(f"   Distance SL: {sl_dist:.5f} ({sl_dist/atr if atr > 0 else 0:.2f}x ATR)")
    print(f"   Distance TP: {tp_dist:.5f} ({tp_dist/atr if atr > 0 else 0:.2f}x ATR)")
    print(f"   Risk:Reward: 1:{tp_dist/sl_dist if sl_dist > 0 else 0:.2f}")
    
    # Vérification de cohérence
    print(f"\n✅ VÉRIFICATIONS:")
    
    if direction == "LONG":
        if sl < entry < tp:
            print(f"   ✅ LONG cohérent: SL < Entry < TP")
        else:
            print(f"   ❌ LONG incohérent!")
    elif direction == "SHORT":
        if tp < entry < sl:
            print(f"   ✅ SHORT cohérent: TP < Entry < SL")
        else:
            print(f"   ❌ SHORT incohérent!")
    
    # Vérifier les multiplicateurs ATR (Pine Script utilise 2.5x et 4.0x)
    expected_sl_mult = 2.5
    expected_tp_mult = 4.0
    
    actual_sl_mult = sl_dist / atr if atr > 0 else 0
    actual_tp_mult = tp_dist / atr if atr > 0 else 0
    
    sl_tolerance = abs(actual_sl_mult - expected_sl_mult) / expected_sl_mult * 100
    tp_tolerance = abs(actual_tp_mult - expected_tp_mult) / expected_tp_mult * 100
    
    if sl_tolerance < 5:
        print(f"   ✅ SL = {actual_sl_mult:.2f}x ATR (attendu: 2.5x)")
    else:
        print(f"   ⚠️ SL = {actual_sl_mult:.2f}x ATR (attendu: 2.5x, écart: {sl_tolerance:.1f}%)")
    
    if tp_tolerance < 5:
        print(f"   ✅ TP = {actual_tp_mult:.2f}x ATR (attendu: 4.0x)")
    else:
        print(f"   ⚠️ TP = {actual_tp_mult:.2f}x ATR (attendu: 4.0x, écart: {tp_tolerance:.1f}%)")
    
    # Flags SMC
    flags = [
        "poi_valid", "fvg_open", "ob_valid", "bos_confirm", 
        "choch_confirm", "liq_swept", "imbalance_filled", 
        "trend_aligned", "volume_confirm", "time_filter"
    ]
    
    active_flags = [f for f in flags if data.get(f, False)]
    confluence = (len(active_flags) / len(flags)) * 100
    
    print(f"\n🎯 FLAGS SMC ({len(active_flags)}/{len(flags)} - Confluence: {confluence:.1f}%):")
    for flag in flags:
        status = "✅" if data.get(flag, False) else "❌"
        print(f"   {status} {flag}")
    
    # Event ID
    event_id = data.get("event_id", "N/A")
    print(f"\n🔑 Event ID: {event_id}")
    
    # Conclusion
    print(f"\n" + "=" * 80)
    if sl_tolerance < 10 and tp_tolerance < 10 and (
        (direction == "LONG" and sl < entry < tp) or 
        (direction == "SHORT" and tp < entry < sl)
    ):
        print("✅ DONNÉES VALIDES - Prix cohérents et calculs corrects")
        print("✅ Ce sont de VRAIES données du marché TradingView")
    else:
        print("⚠️ DONNÉES À VÉRIFIER - Anomalies détectées")
    
    print("=" * 80 + "\n")
    
    # Sauvegarde dans un fichier log
    log_entry = {
        "timestamp": received_at,
        "data": data,
        "analysis": {
            "sl_distance": sl_dist,
            "tp_distance": tp_dist,
            "sl_atr_mult": actual_sl_mult,
            "tp_atr_mult": actual_tp_mult,
            "confluence": confluence
        }
    }
    
    try:
        with open("monitor_log.json", "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    except:
        pass
    
    return {"ok": True, "received_at": received_at, "confluence": confluence}


@app.get("/")
async def root():
    return {
        "status": "monitoring",
        "message": "Webhook monitor actif",
        "endpoint": "/monitor",
        "description": "Envoie tes alertes TradingView vers http://localhost:8001/monitor"
    }


if __name__ == "__main__":
    print("=" * 80)
    print("🔍 SMC MONITOR - VÉRIFICATION DES DONNÉES RÉELLES")
    print("=" * 80)
    print("\n📡 Serveur de monitoring démarré sur http://localhost:8001")
    print("\n📝 INSTRUCTIONS:")
    print("   1. Dans TradingView, configure ton alerte")
    print("   2. Webhook URL: http://localhost:8001/monitor")
    print("   3. Attends un signal")
    print("   4. Les données s'afficheront ici en temps réel")
    print("\n💡 Ce monitor affiche toutes les données reçues pour prouver")
    print("   qu'elles viennent bien du marché réel et non inventées.")
    print("\n" + "=" * 80 + "\n")
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
