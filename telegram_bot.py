import requests
from config import TOKEN_TELEGRAM, CHAT_ID

def enviar_foto(msg, imagen_url):
    url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendPhoto"
    r = requests.post(url, data={
        "chat_id": CHAT_ID,
        "photo": imagen_url,
        "caption": msg,
        "parse_mode": "HTML"
    }, timeout=10)
    return r.status_code == 200