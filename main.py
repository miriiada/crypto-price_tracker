import requests

url = 'https://api.coingecko.com/api/v3/coins/markets'
params = {'vs_currency': 'usd', 'per_page': 5}
response = requests.get(url, params=params)
data = response.json()

for coin in data:
    print(f"{coin['name']}: ${coin['current_price']}")

