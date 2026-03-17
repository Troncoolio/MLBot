from urllib.parse import urlencode
from config import MATT_TOOL

def agregar_afiliado(link):
    link_limpio = link.split("#")[0].split("?")[0]
    params = urlencode({
        "matt_tool": MATT_TOOL,
        "matt_word": "",
        "matt_source": "copy_link",
        "matt_campaign": "native-ads"
    })
    return f"{link_limpio}?{params}"