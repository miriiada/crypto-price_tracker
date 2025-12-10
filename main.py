import requests
import sqlite3
from datetime import datetime
import time
import csv
import json
from telegram import Bot
import asyncio
import config

# ============== SETTINGS =================
API_URL = 'https://api.coingecko.com/api/v3/coins/markets'
DATABASE = 'crypto_price.db'
TOP_COINS = 20 # Coins price

# ============== DTABASE FUNCTIONS ================

def init_database():
    """Create DB and table (if doesn't exist)"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Create table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        coin_id TEXT NOT NULL,
        coin_name TEXT NOT NULL,
        symbol TEXT NOT NULL,
        price_usd REAL NOT NULL,
        market_cap REAL,
        volume_24h REAL,
        price_change_24h REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()
    print(f"✓  Data Base '{DATABASE}' created")

def save_prices(coins_data):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    saved_count = 0

    for coin in coins_data:
        cursor.execute('''
                        INSERT INTO prices (coin_id, coin_name, symbol, price_usd, market_cap, volume_24h, price_change_24h)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            coin['id'],
                            coin['name'],
                            coin['symbol'],
                            coin['current_price'],
                            coin['market_cap'],
                            coin['total_volume'],
                            coin['price_change_percentage_24h']
                        ))
        saved_count += 1

    conn.commit()
    conn.close()

    print(f"✓ Saved {saved_count} records in the database")
    return saved_count

def get_latest_prices(limit=10):
    """Get last from database"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''
                    SELECT coin_name, price_usd, price_change_24h, timestemp
                    FROM prices
                    ORDER BY timestep DESC
                    LIMIT ?
                    ''', (limit,))

    results = cursor.fetchall()
    conn.close()

    return results


def get_price_history(coin_id, hours=24):
    """Get history price a specific coin for N hours"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''
                    SELECT price_usd, timestamp
                    FROM prices
                    WHERE coin_ID = ?
                    AND timestamp >= datetime('now', '-' || ? || ' hours')
                    ORDER BY timestamp ASC
                    ''', (coin_id, hours))

    results = cursor.fetchall()
    conn.close()

    return results

# =============== API FUNCTIONS =================

def fetch_crypto_data():
    """Get data from CoinGecko API"""
    try:
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': TOP_COINS,
            'page': 1,
            'sparkline': False
        }

        response = requests.get(API_URL, params=params)
        response.raise_for_status() # Check on error HTTP

        data = response.json()
        print(f"✓ Get data on {len(data)} coins")
        return data

    except requests.exceptions.RequestException as e:
        print(f"✗ Error for get data: {e}")
        return None

# =============== DISPLAY FUNCTION ================

def display_current_prices(coins_data):
    """Display the current price Beautifully"""
    print("\n" + "=" * 70)
    print(f"{'COIN':<20} {'PRICE (USD)':<15} {'CHANGE 24h':<15}")
    print("=" * 70)

    for coin in coins_data[:10]: # Show top-10
        name = coin['name']
        price = coin['current_price']
        change = coin['price_change_percentage_24h']

        # Color for change (emulation)
        change_symbol = "📈" if change > 0 else "📉"

        print(f"{name:<20} ${price:<14,.2f} {change_symbol} {change:>6.2f}%")

    print("=" * 70 + "\n")

def display_history(coin_id='bitcoin'):
    """Show history price coin"""
    history = get_price_history(coin_id, hours=24)

    if not history:
        print(f"No data for {coin_id}")
        return

    print(f"\n📊 History price {coin_id.upper()} for last 24 hours:")
    print("-" * 50)

    for price, timestamp in history:
        print(f"{timestamp}: ${price:,.2f}")

    # Calculate changes
    if len(history) >= 2:
        first_price = history[0][0]
        last_price = history[-1][0]
        change = ((last_price - first_price) / first_price) * 100

        print("-" * 50)
        print(f"Change: {change:+.2f}% (${first_price:,.2f} → ${last_price:,.2f}")

    print()

# ================== ANALYTICS FUNCTION ===================

def get_coin_statistics(coin_id, hours=24):
    """Get statistics on a coin for a period"""
    history = get_price_history(coin_id, hours)

    if not history:
        return None

    prices = [price for price, timestamp in history]

    stats = {
        'coin_id': coin_id,
        'period_hours': hours,
        'data_points': len(prices),
        'current_price': prices[-1],
        'avg_price': sum(prices) / len(prices),
        'min_price': min(prices),
        'max_price': max(prices),
        'price_change': prices[-1] - prices[0],
        'price_change_percent': ((prices[-1] - prices[0]) / prices[0]) * 100 if prices[0] != 0 else 0,
        'volatility': max(prices) - min(prices)
    }

    return stats


def display_statistics(coin_id='bitcoin', hours=24):
    """Beautiful show statistics"""
    stats = get_coin_statistics(coin_id, hours)

    if not stats:
        print(f"\n️⚠️ insufficient data for {coin_id}")
        print(f"💡 Advice: run script several times with an interval of 1 hour")
        return

    print(f"\n📊 STATISTICS: {coin_id.upper()}")
    print(f"⏰ Period: {hours} hours")
    print(f"📈 Dot stats: {stats['data_points']}")
    print("-" * 50)
    print(f"Current price:      ${stats['current_price']:,.2f}")
    print(f"Avg price:          ${stats['avg_price']:,.2f}")
    print(f"Min:                ${stats['min_price']:,.2f}")
    print(f"Max:                ${stats['max_price']:,.2f}")
    print(f"Change:             ${stats['price_change']:+,.2f} ({stats['price_change_percent']:+.2f}%)")
    print(f"Volatility:         ${stats['volatility']:,.2f}")
    print("-" * 50 + "\n")

# ================ EXPORT FUNCTIONS =====================

def export_to_csv(coin_id, hours=24, filename=None):
    """Export history in CSV"""
    history = get_price_history(coin_id, hours)

    if not history:
        print("No data for export")
        return

    if not filename:
        filename = f"{coin_id}_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Price USD', 'Timestamp'])
        writer.writerows(history)

    print(f"✓ Exporting in {filename}")
    return filename

def export_to_json(coin_id, hours=24, filename=None):
    """Export statistic in JSON"""
    stats = get_coin_statistics(coin_id, hours)
    history = get_price_history(coin_id, hours)

    if not stats:
        print("Not result")
        return

    if not filename:
        filename = f" {coin_id}_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        data = {
            'statistics': stats,
            'history': [
                {'price': price, 'timestamp': timestamp}
                for price, timestamp in history
            ]
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print(f"✓ Exporting if {filename}")
        return filename

# =============== TELEGRAM ALERTS ================

async def send_telegram_alert(message):
    """Send message in Telegram"""
    try:
        bot = Bot(token=config.TELEGRAM_TOKEN)
        await bot.send_message(
            chat_id=config.TELEGRAM_CHAT_ID,
            text=message,
            parse_mode='HTML'
        )
        print(f"✓ Alert send in Telegram")
        return True
    except Exception as e:
        print(f"✗ Error Telegram {e}")
        return False

def check_alerts(coins_data):
    """Checks conditions for alert"""
    alerts = []

    for coin in coin_data:
        change = coin['price_change_percentage_24h']

        # Alert if change exceeds threshold
        if abs(change) >= config.ALERT_PRICE_CHANGE_PERCENT:
            direction = "📈 Up" if change > 0 else "📉 Down"

            alert = {
                'coin': coin['name'],
                'symbol': coin['symbol'].upper(),
                'price': coin['current_price'],
                'change': change,
                'direction': direction
            }
            alerts.append(alert)

    return alerts

async def process_alerts(alerts):
    """Processes and sends alerts"""
    if not alerts:
        print("ℹ️  No alerts")
        return

    print("f🚨 Alerts found: {len(alerts)}")

    for alert in alerts:
        message = f"""
🚨 <b>CRYPTO ALERT!</b>

{alert['direction']}       
<b>{alert['coin']} ({alert['symbol']}</b>

💰 Price: ${alert['price']:,.2f}
📊 Change: {alert['change']:+.2f}%
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
        await send_telegram_alert(message)
        await asyncio.sleep(1) # Delay between messages

# ================= MAIN ====================

def main():
    import argparse

    # CLI arguments
    parser = argparse.ArgumentParser(description='Crypto Price Tracker')
    parser.add_argument('--coin', default='bitcoin', help='Coin ID (default: bitcoin)')
    parser.add_argument('--hours', type=int, default=24, help='History period in hours')
    parser.add_argument('--export', choices=['csv', 'json', 'both'], help='Export format')
    parser.add_argument('--stats-only', action='store_true', help='Show only statistics')
    args = parser.parse_args()

    print("\n🚀 Crypto Price Tracker v0.3")
    print(f"⏰ Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # initialization DB
    init_database()

    # Else only statistics
    if args.stats_only:
        display_statistics(args.coin, args.hours)
        if args.export:
            if args.export in ['CSV', 'both']:
                export_to_csv(args.coin, args.hours)
            if args.export in ['json', 'both']:
                export_to_json(args.coin, args.hours)
        return

    # Base mod: Get new DATA
    print("\n📡 Get data")
    coins_data = fetch_crypto_data()

    if coins_data:
        display_current_prices(coins_data)
        print("💾 Saving...")
        save_prices(coins_data)

        print("\n🔔 Check ")

    # Show statistics for chosen coin
    display_statistics(args.coin, args.hours)

    # Export if needed
    if args.export:
        if args.export in ['csv', 'both']:
            export_to_csv(args.coin, args.hours)
        if args.export in ['json', 'both']:
            export_to_json(args.coin, args.hours)

    print("✅ Ready!\n")


if __name__ == '__main__':
    main()









































