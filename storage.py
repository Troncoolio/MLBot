import json, os

ARCHIVO = os.getenv("STORAGE_PATH", "enviados.json")

def cargar_enviados():
    if os.path.exists(ARCHIVO):
        with open(ARCHIVO, "r") as f:
            return set(json.load(f))
    return set()

def guardar_enviados(enviados):
    with open(ARCHIVO, "w") as f:
        json.dump(list(enviados), f)