import unicodedata
import re

EXCEPCIONES_SCB = {
    "aguas calientes scb",
    "barrancas scb",
    "las delicias scb"
}

SUFIJOS_ELIMINAR = [
    "scb", "dgt", "mvt", "mtv", "mv", "dg", "mvto", "dgto", "mvtos", "dgtes", "mvtas", "dgtes"
]

SUFIJOS_FLEXIBLES = [
    "mtso nuevo", "nuevo"
]

# Mapeo manual para casos especiales de equivalencia
MAPEO_EQUIVALENCIAS = {
    "prolongacion 5ta av": "prolongacion 5ta avenida",
    "prolongacion 5ta avenida": "prolongacion 5ta avenida",
    "cc rodeo": "cc el rodeo",
    "los naranjos": "los naranjos and",
    "moralito": "el moralito",
    "lagunillas": "lagunillas and",
    "sto domingo mupate": "santo domingo mupate",
    "el vigia ii": "el vigia",
    # Nuevas equivalencias agregadas:
    "punta de piedra andes": "punta de piedras (and)",
    "u los colorados": "metrosite colorados",
    "sta barbara barinas centro": "santa barbara de barinas centro",
}

def normalizar_nombre(nombre):
    nombre = nombre.strip()
    # Elimina prefijos UL_ y GUL_
    nombre = re.sub(r'^(ul_|gul_)+', '', nombre, flags=re.IGNORECASE)
    # Elimina dobles guiones bajos, guiones y espacios
    nombre = nombre.replace("_", " ").replace("-", " ").lower().strip()
    nombre = re.sub(r'\s+', ' ', nombre)
    # Elimina tildes y normaliza
    nombre = "".join(
        c for c in unicodedata.normalize("NFD", nombre)
        if unicodedata.category(c) != "Mn"
    )
    nombre = nombre.strip()
    # Si el nombre es una excepción, no eliminar sufijos
    if nombre in EXCEPCIONES_SCB:
        return nombre
    # Elimina sufijos tipo SCB, DGT, etc. (palabra al final)
    nombre = re.sub(r'\s+(' + '|'.join(SUFIJOS_ELIMINAR) + r')$', '', nombre)
    # Elimina sufijos flexibles como "mtso nuevo", "nuevo" (palabra o frase al final)
    nombre = re.sub(r'\s+(' + '|'.join(SUFIJOS_FLEXIBLES) + r')$', '', nombre)
    nombre = nombre.strip()
    # Mapeo manual para equivalencias conocidas
    if nombre in MAPEO_EQUIVALENCIAS:
        return MAPEO_EQUIVALENCIAS[nombre]
    return nombre if nombre else None
