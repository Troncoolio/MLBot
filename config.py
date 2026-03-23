from dotenv import load_dotenv
import os

load_dotenv()

TOKEN_TELEGRAM = os.getenv("TOKEN_TELEGRAM")
CHAT_ID = os.getenv("CHAT_ID")
MATT_TOOL = os.getenv("MATT_TOOL")

DESCUENTO_MINIMO = 10

INTERVALO_MINUTOS = 360

MAX_PRODUCTOS_PER_ROUND = 10

CATEGORIAS = [
    "iphone", "samsung", "laptop", "audifonos",
    "television", "tablet", "playstation", "xbox",
    "nintendo-switch", "smartwatch", "monitor",
    "ipad", "macbook", "cafetera", "licuadora"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "es-MX,es;q=0.9",
}