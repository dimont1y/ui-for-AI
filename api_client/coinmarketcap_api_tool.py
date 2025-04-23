import requests

from apis.config import COINMARKETCAP_API_KEY

from agents import function_tool

BASE_URL = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'

@function_tool
def get_crypto_data(symbol:str):
    """Отримати поточну інформацію про криптовалюту за символом (наприклад, BTC, ETH, DOGE)"""
    headers = {'Accepts': 'application/json', 'X-CMC_PRO_API_KEY': COINMARKETCAP_API_KEY}
    params = {'symbol': symbol.upper(), 'convert': 'USD'}  # upper() щоб працювало і з "btc", і з "BTC"

    try:
        response = requests.get(BASE_URL, headers=headers, params=params)
        response.raise_for_status()  # Викличе помилку, якщо поганий статус код
        data = response.json()

        if 'data' in data and symbol.upper() in data['data']:
            crypto = data['data'][symbol.upper()]['quote']['USD']
            return {
                'symbol': symbol.upper(),
                'price': crypto['price'],
                '1h_change': crypto['percent_change_1h'],
                '24h_change': crypto['percent_change_24h'],
                '7d_change': crypto['percent_change_7d'],
                'market_cap': crypto['market_cap'],
                'volume_24h': crypto['volume_24h'],
                'circulating_supply': data['data'][symbol.upper()]['circulating_supply']
            }
        else:
            return {'error': f'Криптовалюта {symbol} не знайдена'}

    except requests.exceptions.RequestException as e:
        return {'error': f'Помилка запиту: {str(e)}'}

@function_tool
def compare_crypto_data(symbol1: str, symbol2: str):
    """Порівняти дві криптовалюти за символами, повертає основні метрики"""
    symbols = f"{symbol1.upper()},{symbol2.upper()}"
    headers = {'Accepts': 'application/json', 'X-CMC_PRO_API_KEY': COINMARKETCAP_API_KEY}
    params = {'symbol': symbols, 'convert': 'USD'}

    try:
        response = requests.get(BASE_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json().get("data", {})

        result = {}
        for sym in [symbol1.upper(), symbol2.upper()]:
            if sym in data:
                quote = data[sym]['quote']['USD']
                result[sym] = {
                    'price': quote['price'],
                    '1h_change': quote['percent_change_1h'],
                    '24h_change': quote['percent_change_24h'],
                    '7d_change': quote['percent_change_7d'],
                    'market_cap': quote['market_cap'],
                    'volume_24h': quote['volume_24h'],
                    'circulating_supply': data[sym]['circulating_supply']
                }
            else:
                result[sym] = {'error': f'{sym} not found'}

        return result

    except requests.exceptions.RequestException as e:
        return {'error': f'Request error: {str(e)}'}

@function_tool
def get_historical_data(symbol: str, days: int):
    """Отримати історичну динаміку криптовалюти за певну кількість днів."""
    headers = {'Accepts': 'application/json', 'X-CMC_PRO_API_KEY': COINMARKETCAP_API_KEY}
    params = {'symbol': symbol.upper(), 'convert': 'USD', 'timespan': f'{days}d'}

    try:
        response = requests.get(BASE_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        if 'data' in data:
            historical_prices = data['data']['prices']
            return historical_prices
        else:
            return {'error': f'Не знайдено історичних даних для {symbol} за {days} днів.'}

    except requests.exceptions.RequestException as e:
        return {'error': f'Помилка запиту: {str(e)}'}

# 🔹 Приклад використання
if __name__ == "__main__":
    crypto = input("Введіть символ криптовалюти (наприклад, BTC, ETH, DOGE): ").strip()
    print(get_crypto_data(crypto))