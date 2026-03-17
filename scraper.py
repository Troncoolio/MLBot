import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from config import DESCUENTO_MINIMO
from afiliados import agregar_afiliado
from telegram_bot import enviar_foto
from storage import cargar_enviados, guardar_enviados
from logger import logger

ya_enviados = cargar_enviados()

def crear_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--lang=es-MX")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.binary_location = "/usr/bin/chromium"  # <- ruta en Railway
    
    driver = webdriver.Chrome(
        service=Service("/usr/bin/chromedriver"),  # <- ruta en Railway
        options=options
    )
    return driver

def buscar_ofertas():
    ofertas = 0
    driver = crear_driver()

    try:
        for pagina in range(1, 6):
            url = f"https://www.mercadolibre.com.mx/ofertas?page={pagina}"
            logger.info(f"Escaneando página {pagina}")
            driver.get(url)
            time.sleep(5)

            for _ in range(5):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            productos = soup.find_all("div", class_="poly-card")
            logger.info(f"  Página {pagina}: {len(productos)} productos")

            for p in productos:
                try:
                    # Título y link
                    titulo_tag = p.find("a", class_="poly-component__title")
                    if not titulo_tag:
                        continue
                    titulo = titulo_tag.text.strip()
                    link = titulo_tag.get("href", "")
                    if not link:
                        continue

                    # Evitar duplicados
                    link_limpio = link.split("#")[0].split("?")[0]
                    if link_limpio in ya_enviados:
                        continue

                    # Imagen
                    imagen_tag = p.find("img", class_="poly-component__picture")
                    imagen_url = imagen_tag.get("src", "") if imagen_tag else ""

                    # Precio actual
                    precio_tag = p.find("div", class_="poly-price__current")
                    if not precio_tag:
                        continue
                    fraccion = precio_tag.find("span", class_="andes-money-amount__fraction")
                    if not fraccion:
                        continue
                    precio = int(fraccion.text.strip().replace(",", "").replace(".", ""))

                    # Precio original
                    precio_original_tag = p.find("s", class_="andes-money-amount--previous")
                    precio_original = None
                    if precio_original_tag:
                        po = precio_original_tag.find("span", class_="andes-money-amount__fraction")
                        if po:
                            precio_original = int(po.text.strip().replace(",", "").replace(".", ""))

                    # Descuento
                    descuento = 0
                    descuento_tag = p.find("span", class_="andes-money-amount__discount")
                    if descuento_tag:
                        texto = descuento_tag.text.strip()
                        # limpia cualquier caracter raro
                        texto_limpio = ''.join(filter(str.isdigit, texto))
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

                except Exception as e:
                    logger.error(f"Error procesando producto: {e}")
                    continue

            time.sleep(3)

    except Exception as e:
        logger.error(f"Error general: {e}")
    finally:
        driver.quit()

    return ofertas