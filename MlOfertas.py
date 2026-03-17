import requests
from bs4 import BeautifulSoup
import time, os 
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
CHAT_ID = "-1003528240329"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "es-MX,es;q=0.9",
}

CATEGORIAS = [
    "iphone 15"
]

ya_enviados = set()

def agregar_afiliado(link):
    link_limpio = link.split("#")[0].split("?")[0]
    params = urlencode({
        "matt_tool": "78642436",
        "matt_word": "",
        "matt_source": "copy_link",
        "matt_campaign": "native-ads"
    })
    return f"{link_limpio}?{params}"

def enviar_telegram_foto(msg, imagen_url):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        r = requests.post(url, data={
            "chat_id": CHAT_ID,
            "photo": imagen_url,
            "caption": msg,
            "parse_mode": "HTML"
        }, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print("Error Telegram:", e)
        return False

def buscar_categoria(query, descuento_minimo=20):
    url = f"https://listado.mercadolibre.com.mx/{query}"
    ofertas = 0

    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        productos = soup.find_all("li", class_="ui-search-layout__item")
        print(f"  [{query}] {len(productos)} productos")

        for p in productos:
            try:
                titulo_tag = p.find("a", class_="poly-component__title")
                if not titulo_tag:
                    continue
                titulo = titulo_tag.text.strip()
                link = titulo_tag.get("href", "")
                if not link:
                    continue

                link_limpio = link.split("#")[0].split("?")[0]
                if link_limpio in ya_enviados:
                    continue

                imagen_tag = p.find("img", class_="poly-component__picture")
                imagen_url = imagen_tag.get("src", "") if imagen_tag else ""

                precio_tag = p.find("div", class_="poly-price__current")
                if not precio_tag:
                    continue
                fraccion = precio_tag.find("span", class_="andes-money-amount__fraction")
                if not fraccion:
                    continue
                precio = int(fraccion.text.strip().replace(",", ""))

                precio_original_tag = p.find("s", class_="andes-money-amount--previous")
                precio_original = None
                if precio_original_tag:
                    po = precio_original_tag.find("span", class_="andes-money-amount__fraction")
                    if po:
                        precio_original = int(po.text.strip().replace(",", ""))

                descuento_tag = p.find("span", class_="andes-money-amount__discount")
                descuento = 0
                if descuento_tag:
                    texto = descuento_tag.text.strip().replace("% OFF", "").replace("%", "")
                    try:
                        descuento = int(texto)
                    except:
                        pass
                elif precio_original and precio_original > 0:
                    descuento = round(100 - (precio / precio_original * 100))

                if descuento >= descuento_minimo:
                    link_afiliado = agregar_afiliado(link)
                    caption = (
                        f"📦 {titulo}\n"
                        f"{'De: $' + f'{precio_original:,}'} a ${precio:,}\n"
                        f"📉 Descuento: {descuento}%\n"
                        f"🔗 {link_afiliado}"
                    )
                    if enviar_telegram_foto(caption, imagen_url):
                        ya_enviados.add(link_limpio)
                        print(f"    ✅ {titulo[:40]} | {descuento}% OFF")
                        ofertas += 1
                        time.sleep(1)

            except Exception:
                continue

    except Exception as e:
        print(f"  Error en {query}: {e}")

    return ofertas

while True:
    print("🔍 Escaneando todas las categorías...")
    total = 0
    for categoria in CATEGORIAS:
        total += buscar_categoria(categoria, descuento_minimo = 15)
        time.sleep(3)
    print("⏳ Esperando 10 minutos...\n")
    time.sleep(600)