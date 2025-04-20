import requests

from agents import function_tool
from apis.config  import ETHERSCAN_API_KEY, BSCSCAN_API_KEY, SOLSCAN_API_KEY

ETHERSCAN_API_KEY=ETHERSCAN_API_KEY
BSCSCAN_API_KEY=BSCSCAN_API_KEY

@function_tool
def explore_token(symbol:str):
    network = network.lower()

    if network == "ethereum":
        url = f"https://api.etherscan.io/api"
        params = {
            "module": "token",
            "action": "tokeninfo",
            "contractaddress": address,
            "apikey": ETHERSCAN_API_KEY
        }
        try:
            response = requests.get(url, params=params)
            data = response.json()
            if data["status"] == "1":
                token_info = data["result"][0]
                return {
                    "name": token_info.get("tokenName"),
                    "symbol": token_info.get("symbol"),
                    "decimals": token_info.get("divisor"),
                    "holders": token_info.get("totalHolders"),
                    "network": "ethereum"
                }
            else:
                return {"error": data.get("result", "Unknown error from Etherscan")}
        except Exception as e:
            return {"error": str(e)}

    elif network == "bsc":
        url = f"https://api.bscscan.com/api"
        params = {
            "module": "token",
            "action": "tokeninfo",
            "contractaddress": address,
            "apikey": BSCSCAN_API_KEY
        }
        try:
            response = requests.get(url, params=params)
            data = response.json()
            if data["status"] == "1":
                token_info = data["result"][0]
                return {
                    "name": token_info.get("tokenName"),
                    "symbol": token_info.get("symbol"),
                    "decimals": token_info.get("divisor"),
                    "holders": token_info.get("totalHolders"),
                    "network": "bsc"
                }
            else:
                return {"error": data.get("result", "Unknown error from BscScan")}
        except Exception as e:
            return {"error": str(e)}

    elif network == "solana":
        url = f"https://public-api.solscan.io/token/meta?tokenAddress={address}"
        headers = {"accept": "application/json"}
        try:
            response = requests.get(url, headers=headers)
            data = response.json()
            if data:
                return {
                    "name": data.get("name"),
                    "symbol": data.get("symbol"),
                    "decimals": data.get("decimals"),
                    "network": "solana"
                }
            else:
                return {"error": "Token not found on Solana"}
        except Exception as e:
            return {"error": str(e)}

    else:
        return {"error": "Unsupported network. Please use ethereum, bsc, or solana."}


if __name__ == "__main__":
    address = input("Введіть адресу токена: ").strip()
    network = input("Оберіть мережу (ethereum / bsc / solana): ").strip().lower()

    result = explore_token.raw_function(address, network)

    print("\n🔎 Результат перевірки токена:")
    if "error" in result:
        print(f"❌ Помилка: {result['error']}")
    else:
        print(f"📛 Назва: {result['name']}")
        print(f"🔤 Символ: {result['symbol']}")
        print(f"🔢 Десяткових: {result['decimals']}")
        if result.get("holders"):
            print(f"👥 Кількість холдерів: {result['holders']}")
        print(f"🌐 Мережа: {result['network']}")


