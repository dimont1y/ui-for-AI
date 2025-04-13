import requests

TOKEN = "REDACTED" # Get your token at @BotFather Telegram bot after bot creation
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

chat_id = 12345678  # Replace with your chat ID. You can get your chat id in @userinfobot


def send_message(text: str) -> None:
    url = BASE_URL + "sendMessage"
    params = {
        "chat_id": chat_id,
        "text": text
    }
    response = requests.get(url, params=params)
    if response.ok:
        print("LOG: Message sent successfully!")
    else:
        print("Failed to send message.")
        print("Response:", response.text)
        raise Exception("Failed to send message.")
