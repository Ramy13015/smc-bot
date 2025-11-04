# 🚀 Guide de Démarrage Rapide - SMC Trading Bot

## ⚡ Démarrage en 3 étapes

### 1️⃣ Lancer le Bot (Local)
```powershell
cd c:\Users\bouga\Desktop\smc-bot
.\start.bat
```

Le serveur démarre sur `http://localhost:8000`

---

### 2️⃣ Vérifier que tout fonctionne

**Option A: Via navigateur**
- Ouvrir `http://localhost:8000/health`
- Vérifier que `"ok": true` et `"telegram_configured": true`

**Option B: Via commande**
```powershell
python test_telegram.py
```
✅ Un message de test sera envoyé sur Telegram

---

### 3️⃣ Configurer TradingView

1. **Ajouter l'indicateur**
   - Ouvrir TradingView
   - Charger le script `smc_high_volume.pine`
   - L'appliquer sur un graphique supporté (BTCUSDT, EURUSD, etc.)

2. **Créer une alerte**
   - Clic droit sur le graphique → **"Créer une alerte"**
   - **Condition:** "SMC Detector - HIGH VOLUME MARKETS"
   - **Options:**
     - Once Per Bar Close
   - **Notifications:**
     - ✅ Webhook URL: `https://smc-gal.onrender.com/tv`
   - **Message de l'alerte:** Laisser vide (Pine Script gère tout)

3. **Créer l'alerte**
   - Cliquer sur "Créer"
   - ✅ L'alerte est active !

---

## 📊 Symboles Supportés

### Crypto Perpetuals (Bybit/Binance)
- BTCUSDT.P, ETHUSDT.P, SOLUSDT.P
- ADAUSDT.P, DOGEUSDT.P, XRPUSDT.P

### Forex (Majors)
- EURUSD, GBPUSD, USDJPY
- AUDUSD, USDCAD

### Precious Metals
- XAUUSD (Gold)

---

## 🎯 Critères de Signal

Le bot envoie un signal uniquement si:
1. ✅ **Confluence ≥ 80%** (minimum 8 flags sur 10)
2. ✅ **Volume confirmé** (au-dessus de la moyenne)
3. ✅ **Tendance alignée** (EMA 21 > EMA 50 > EMA 200)
4. ✅ **Timeframe valide** (pas d'heures creuses pour Forex)

### Les 10 Flags SMC
1. POI Valid (Point d'Intérêt)
2. FVG Open (Fair Value Gap)
3. OB Valid (Order Block)
4. BOS Confirm (Cassure de Structure)
5. CHOCH Confirm (Changement de Caractère)
6. Liq Swept (Liquidité Balayée)
7. Imbalance Filled (Déséquilibre Comblé)
8. Trend Aligned (Tendance Alignée)
9. Volume Confirm (Volume Confirmé)
10. Time Filter (Filtre Horaire)

---

## 💬 Format Message Telegram

```
🟢 SMC SIGNAL - LONG BTCUSDT.P

📊 Confluence Score: 90.0%
📈 Timeframe: 15
💰 Entry: 50000.00000
🛑 Stop Loss: 49375.00000
🎯 Take Profit: 51000.00000
📏 Position Size: 0.10
⚖️ Risk:Reward: 1:2.50

🎯 Active Flags:
✅ Poi Valid
✅ Fvg Open
✅ Ob Valid
✅ BOS Confirm
✅ CHOCH Confirm
✅ Liq Swept
✅ Imbalance Filled
✅ Trend Aligned
✅ Volume Confirm

📢 @MonBotFibo
```

---

## 🛠️ Commandes Utiles

### Démarrer le bot
```powershell
.\start.bat
```

### Tester Telegram
```powershell
python test_telegram.py
```

### Vérifier la santé du bot
```powershell
curl http://localhost:8000/health
```

### Arrêter le bot
Appuyer sur `CTRL+C` dans le terminal

---

## 🔍 Dépannage

### Le bot ne démarre pas
```powershell
# Réinstaller les dépendances
python -m pip install -r requirements.txt --upgrade
```

### Telegram ne reçoit pas les messages
```powershell
# Vérifier la configuration
python test_telegram.py
```

### Les alertes TradingView ne fonctionnent pas
1. Vérifier que le webhook URL est correct
2. Vérifier que l'alerte est active (icône cloche dans TradingView)
3. Vérifier les logs du serveur

---

## 📝 Logs et Surveillance

Les logs s'affichent dans le terminal où le bot tourne:
- `[INFO]` : Opérations normales
- `[WARNING]` : Avertissements (signal rejeté, etc.)
- `[ERROR]` : Erreurs (problème Telegram, etc.)

---

## 🌐 Déploiement Production (Render.com)

Le bot est préconfiguré pour Render.com:

1. **Créer un compte sur Render.com**
2. **Créer un nouveau Web Service**
   - Repository: Connecter votre repo GitHub
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. **Configurer les variables d'environnement**
   - Copier toutes les valeurs de `.env`
4. **Déployer**
   - URL générée: `https://your-app.onrender.com`
   - Mettre à jour le webhook TradingView avec cette URL

---

## ✅ Checklist avant Production

- [ ] Bot démarre sans erreur
- [ ] Test Telegram réussi
- [ ] Au moins une alerte TradingView configurée
- [ ] Webhook URL correct dans TradingView
- [ ] Bot déployé sur Render.com (ou serveur 24/7)
- [ ] Surveillance active des signaux

---

**Status:** ✅ Bot 100% opérationnel  
**Support:** Vérifier `STATUS.md` pour plus de détails
