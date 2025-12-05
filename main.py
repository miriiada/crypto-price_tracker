import requests
import sqlite3
from datetime import datetime
import time

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

# ================= MAIN ====================

def main():
    print("\n🚀 Crypto Price Tracker v0.2")
    print(f"⏰ Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # 1. initialization DB
    init_database()

    # 2. Get DATA for API
    print("\n📡 Get DATA for CoinGecko...")
    coins_data = fetch_crypto_data()

    if not coins_data:
        print("Can't get data. End connect.")
        return

    # 3. Show price now
    display_current_prices(coins_data)

    # 4. Save in DB
    print("💾 Save in DB...")
    save_prices(coins_data)

    # 5. Show history Bitcoin (Example)
    print("\n📈 Checking history...")
    display_history('bitcoin')

    print("✅ Ready!\n")

if __name__ == '__main__':
    main()









































