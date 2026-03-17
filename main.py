import time, find_chrome
from config import INTERVALO_MINUTOS
from scraper import buscar_ofertas  # ← ya no es buscar_categoria
from logger import logger

while True:
    logger.info("🔍 Escaneando ofertas de MercadoLibre...")
    total = buscar_ofertas()
    logger.info(f"✅ Ronda completa. Ofertas enviadas: {total}")
    logger.info(f"⏳ Esperando {INTERVALO_MINUTOS} minutos...")
    time.sleep(INTERVALO_MINUTOS * 60)