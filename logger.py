import logging, os

LOG_PATH = os.getenv("LOG_PATH", "bot.log")  # puedes cambiar en EC2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)