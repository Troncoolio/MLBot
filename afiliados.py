from urllib.parse import urlencode
import os

MATT_TOOL = os.getenv("MATT_TOOL", "78642436")
MATT_WORD = "caan3223614"

def agregar_afiliado(link):
    link_limpio = link.split("#")[0].split("?")[0]
    params = urlencode({
        "matt_tool": MATT_TOOL,
        "matt_word": MATT_WORD,
        "matt_source": "copy_link",
        "matt_campaign": "native-ads"
    })
    return f"{link_limpio}?{params}"