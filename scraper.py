import time
import os
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from config import DESCUENTO_MINIMO, MAX_PRODUCTOS_PER_ROUND
from afiliados import agregar_afiliado
from telegram_bot import enviar_foto
from storage import cargar_enviados, guardar_enviados
from logger import logger

ya_enviados = cargar_enviados()

def crear_browser(p):
    es_railway = os.getenv("RAILWAY_ENVIRONMENT") is not None
    browser = p.chromium.launch(
        headless=es_railway,
        args=[
            "--no-sandbox",
              "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
            "--lang=es-MX"
        ]
    )
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        locale="es-MX"
    )
    return browser, context  # <- regresa los dos

def buscar_ofertas():
    ofertas = 0

    with sync_playwright() as p:
        browser, context = crear_browser(p)  # <- recibe los dos
        page = context.new_page()  # <- usa context, no browser

        try:
            for pagina in range(1, 6):
                url = f"https://www.mercadolibre.com.mx/ofertas?page={pagina}"
                logger.info(f"Escaneando página {pagina}")
                page.goto(url, timeout=60000, wait_until="domcontentloaded")
                page.wait_for_timeout(5000)

                for _ in range(5):
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    page.wait_for_timeout(2000)

                soup = BeautifulSoup(page.content(), "html.parser")
                productos = soup.find_all("div", class_="poly-card")
                logger.info(f"  Página {pagina}: {len(productos)} productos")

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
                        precio = int(fraccion.text.strip().replace(",", "").replace(".", ""))

                        precio_original_tag = p.find("s", class_="andes-money-amount--previous")
                        precio_original = None
                        if precio_original_tag:
                            po = precio_original_tag.find("span", class_="andes-money-amount__fraction")
                            if po:
                                precio_original = int(po.text.strip().replace(",", "").replace(".", ""))

                        descuento = 0
                        descuento_tag = p.find("span", class_="andes-money-amount__discount")
                        if descuento_tag:
                            texto_limpio = ''.join(filter(str.isdigit, descuento_tag.text.strip()))
                            if texto_limpio:
                                descuento = int(texto_limpio)
                        elif precio_original and precio_original > 0:
                            descuento = round(100 - (precio / precio_original * 100))

                        logger.info(f"    {titulo[:40]} | ${precio:,} | {descuento}% OFF")

                        if descuento >= DESCUENTO_MINIMO:
                            link_afiliado = agregar_afiliado(link)
                            caption = (
                                f"📦 {titulo}\n"
                                f"{'De: $' + f'{precio_original:,}' + ' a ' if precio_original else ''}"
                                f"${precio:,}\n"
                                f"📉 Descuento: {descuento}%\n"
                                f"🔗 {link_afiliado}"
                            )
                            if enviar_foto(caption, imagen_url):
                                ya_enviados.add(link_limpio)
                                guardar_enviados(ya_enviados)
                                logger.info(f"✅ ENVIADO: {titulo[:40]} | {descuento}% OFF")
                                ofertas += 1
                                time.sleep(1)

                                if ofertas >= MAX_PRODUCTOS_PER_ROUND:
                                    logger.info(f"Limite de {MAX_PRODUCTOS_PER_ROUND}")
                                    return ofertas

                    except Exception as e:
                        logger.error(f"Error procesando producto: {e}")
                        continue

                time.sleep(3)

        except Exception as e:
            logger.error(f"Error general: {e}")
        finally:
            browser.close()

    return ofertas