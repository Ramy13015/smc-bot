# SMC Trading Bot

Complete Smart Money Concepts Trading Bot with TradingView webhook integration.

## 🚀 Quick Deploy on Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### Render Configuration:

**Build Command:** `pip install -r requirements.txt`

**Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Environment Variables:
```
TELEGRAM_TOKEN=8291225729:AAGtKgfUiK7yQLUxH1F12xtj3rpwpZKTudg
TELEGRAM_CHAT_ID=1434819878
BASE_EQUITY=5000
RISK_PCT=0.01
CONFLUENCE_THRESH=0.80
ATR_SL_MULT=1.5
ATR_TP_MULT=2.0
ANTI_SPAM_TTL=300
```

## 📋 Features

✅ **SMC Confluence Scoring** - 10 weighted flags for signal quality  
✅ **Critical Flag Validation** - poi_valid & fvg_open required  
✅ **Risk Management** - Auto SL/TP calculation with ATR  
✅ **Position Sizing** - 1% risk per trade with dynamic sizing  
✅ **Telegram Notifications** - Rich formatted messages  
✅ **Anti-Duplicate** - TTL-based signal filtering  
✅ **FastAPI** - RESTful webhooks with validation  

## 🔗 Endpoints

- `POST /tv` - TradingView webhook (main)
- `GET /health` - Health check with config
- `GET /stats` - Bot statistics
- `POST /clear-cache` - Admin cache management

## 📊 SMC Flag Weights

| Flag | Weight | Required |
|------|--------|----------|
| poi_valid | 0.25 | ✅ Critical |
| fvg_open | 0.15 | ✅ Critical |
| ob_valid | 0.12 | |
| bos_confirm | 0.10 | |
| choch_confirm | 0.08 | |
| liq_swept | 0.08 | |
| imbalance_filled | 0.07 | |
| trend_aligned | 0.06 | |
| volume_confirm | 0.05 | |
| time_filter | 0.04 | |

**Minimum Score:** 80% for signal execution

## 🎯 Usage

1. Deploy to Render with above configuration
2. Get webhook URL: `https://your-app.onrender.com/tv`
3. Configure TradingView alert with JSON payload
4. Receive signals in Telegram @MonBotFibo

## 📝 TradingView JSON Payload

```json
{
  "event_id": "EURUSD_1699876543_12345",
  "symbol": "EURUSD",
  "timeframe": "1h",
  "direction": "LONG",
  "price_ctx": {
    "entry": 1.0850,
    "ref_high": 1.0900,
    "ref_low": 1.0800
  },
  "atr": 0.0025,
  "flags": {
    "poi_valid": true,
    "fvg_open": true,
    "ob_valid": true,
    "bos_confirm": false,
    "choch_confirm": true,
    "liq_swept": false,
    "imbalance_filled": true,
    "trend_aligned": true,
    "volume_confirm": false,
    "time_filter": true
  }
}
```

## 🏗️ Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment config
cp .env.example .env

# Run locally
python -m app.main
```

Server runs on `http://localhost:8000`

## 📚 Project Structure

```
smc-bot/
├── app/
│   ├── __init__.py      # Package init
│   ├── main.py          # FastAPI application
│   ├── models.py        # Pydantic data models
│   ├── config.py        # Environment configuration
│   ├── smc.py           # SMC scoring & risk management
│   ├── notifier.py      # Telegram messaging
│   └── utils.py         # Anti-duplicate utilities
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

---

**Repository:** https://github.com/Ramy13015/smc-bot  
**Telegram:** @MonBotFibo  
**License:** MIT