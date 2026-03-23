from urllib.parse import urlencode, quote
import os

MATT_TOOL = os.getenv("MATT_TOOL", "78642436")
MATT_WORD = "caan3223614"

def agregar_afiliado(link):
    link_limpio = link.split("#")[0].split("?")[0]
    params = urlencode({
        "matt_word": MATT_WORD,
        "matt_tool": MATT_TOOL,
        "forceInApp": "true",
        "url": link_limpio  # <- el producto va aquí
    })
    return f"https://www.mercadolibre.com.mx/social/{MATT_WORD}?{params}"