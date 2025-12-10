# 🚀 Crypto Price Tracker

Real-time cryptocurrency price monitoring system with Telegram alerts, historical data analysis, and data export capabilities.

## ✨ Features

- 📊 **Real-time price tracking** for top 20 cryptocurrencies
- 💾 **SQLite database** for historical data storage  
- 📈 **Statistical analysis**: average, min/max, volatility
- 🔔 **Telegram alerts** when price changes exceed threshold
- 📤 **Data export** to CSV and JSON formats
- 🖥️ **CLI interface** with customizable parameters

## 🛠️ Technologies

- **Python 3.9+**
- **SQLite** - database
- **Requests** - API calls
- **Python-telegram-bot** - notifications
- **CoinGecko API** - price data source

## 📦 Installation

1. Clone repository:
   - git clone https://github.com/YOUR_USERNAME/crypto-price-tracker.git
   - cd crypto-price-tracker
2. Create virtual environment:
   - python -m venv .venv
   - .venv\Scripts\activate # Windows
   - source .venv/bin/activate # Linux/Mac
3. Install dependencies:
   - pip install -r requirements.txt
4. Configure Telegram bot:
   - Create bot via [@BotFather](https://t.me/BotFather)
   - Copy token
   - Get your Chat ID via [@userinfobot](https://t.me/userinfobot)

5. Create `config.py`:
   - TELEGRAM_TOKEN = "your_bot_token_here"
   - TELEGRAM_CHAT_ID = "your_chat_id_here"
   - ALERT_PRICE_CHANGE_PERCENT = 5.0
## 🚀 Usage

### Basic run (fetch prices + save to DB):
   - python main.py
### Show statistics for specific coin:
   - python main.py --coin ethereum --hours 24
### Export data:
   - python main.py --coin bitcoin --export csv
   - python main.py --coin ethereum --export json
### Statistics only (no new data):
   - python main.py --stats-only --coin solana

## 📊 Screenshots

*Add screenshots here after creating them*

## 🔮 Future Improvements

- [ ] Web dashboard with charts
- [ ] Support for more exchanges
- [ ] Price prediction using ML
- [ ] Portfolio tracking
- [ ] Multi-user support

## 📝 License

MIT License - free to use and modify

## 👤 Author

Miriiada - [GitHub](https://github.com/miriiada) | [LinkedIn](your_linkedin)

---

**Built with 💻 and ☕ during Python learning journey**





