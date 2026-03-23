import time, schedule
from config import INTERVALO_MINUTOS
from scraper import buscar_ofertas  # ← ya no es buscar_categoria
from logger import logger

def ronda():
    logger.info("Escanenado")
    total = buscar_ofertas()
    logger.info(f"Ronda completa ofertas {total}")

    schedule.every().day.at("8:30").do(ronda)
    schedule.every().day.at("10:40").do(ronda)
    schedule.every().day.at("13:30").do(ronda)
    schedule.every().day.at("19:30").do(ronda)

    logger.info("Iniciado, espera horario")


while True:
    schedule.run_pending()
    time.sleep(60)