# Plevee - Multi-Asset Automated Trading Platform

A professional trading platform supporting stocks, crypto, and prediction markets with automated strategy execution.

## Features

- 🎯 **Multi-Asset Trading**: Stocks (Webull), Crypto (Binance), Prediction Markets (Polymarket)
- 🤖 **Automated Strategies**: Momentum, Mean Reversion with TA-Lib indicators
- 📊 **Real-Time Data**: Live quotes, historical charts, market analysis
- 🔄 **Background Tasks**: Celery-powered strategy execution
- 💼 **Portfolio Management**: Track positions, P&L, trade history
- 🔐 **Secure**: JWT authentication, encrypted credentials
- 🖥️ **Desktop App**: Beautiful Flutter macOS app
- 🔄 **Auto-Update**: Seamless app updates via GitHub releases

## Quick Start

### Backend

```bash
cd Plevee
docker-compose up -d
```

Services:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Flower: http://localhost:5555

### Desktop App

```bash
cd plevee_desktop
flutter run -d macos
```

## Tech Stack

**Backend:**
- FastAPI + PostgreSQL + Redis
- Celery for background tasks
- Webull, Polymarket, CCXT SDKs
- TA-Lib for technical analysis

**Frontend:**
- Flutter Desktop (macOS)
- Riverpod state management
- Material Design 3

## Documentation

See `/docs` folder for detailed guides:
- [Quick Start](docs/quick_start.md)
- [Production Setup](docs/production_implementation.md)
- [Auto-Update System](docs/auto_update_guide.md)
- [Polymarket Guide](docs/polymarket_guide.md)

## License

MIT
