"""Servicio de "Consejo del dia" basado en clima real (Open-Meteo API).

Feature "plus" del catalogo: consulta el clima actual de la ciudad de la
tienda (Bogota, por defecto) contra la API publica y gratuita de Open-Meteo
(https://open-meteo.com, no requiere API key) y traduce temperatura +
condicion climatica en una recomendacion corta de cuidado de mascotas
("hace calor: dale agua fresca", "va a llover: evita el paseo largo", etc).

Ver docs/api_clima_mascotas.md para la documentacion completa (como se
aplico, para que, pros/contras y donde encaja en el diagrama de capas).
"""

import json
import time
import urllib.request
from urllib.error import URLError

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# Bogota por defecto: la tienda no pide aun la ubicacion del usuario, asi
# que se usa la ciudad base de la operacion. Si en el futuro se guarda la
# ciudad del usuario (ver User.city), este valor puede reemplazarse por la
# de cada usuario sin cambiar el resto del servicio.
DEFAULT_LAT = 4.7110
DEFAULT_LON = -74.0721
DEFAULT_CITY = "Bogota"

REQUEST_TIMEOUT_SECONDS = 4
CACHE_TTL_SECONDS = 30 * 60  # 30 minutos: evita golpear la API externa en cada visita

# codigos WMO (weather_code de Open-Meteo) agrupados en familias simples
_CLEAR = {0, 1}
_CLOUDY = {2, 3}
_FOG = {45, 48}
_RAIN = {51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82}
_STORM = {95, 96, 99}
_SNOW = {71, 73, 75, 77, 85, 86}

_cache: dict = {"data": None, "fetched_at": 0.0}


def _condition_label(code: int) -> str:
    if code in _CLEAR:
        return "despejado"
    if code in _CLOUDY:
        return "nublado"
    if code in _FOG:
        return "niebla"
    if code in _RAIN:
        return "lluvia"
    if code in _STORM:
        return "tormenta"
    if code in _SNOW:
        return "nieve"
    return "variable"


def _build_tip(temperature: float, condition: str) -> str:
    """Traduce temperatura + condicion en un consejo breve y accionable."""
    if condition in ("lluvia", "tormenta"):
        return (
            "Va a llover hoy: acorta el paseo y sécale bien las patas a tu "
            "mascota al volver para evitar hongos entre los dedos."
        )
    if condition == "nieve":
        return (
            "Temperaturas muy bajas: protege las almohadillas de las patas "
            "con botines o vaselina antes de salir."
        )
    if temperature >= 27:
        return (
            "Hace calor hoy: asegúrate de que tu mascota tenga agua fresca "
            "disponible todo el día y evita pasearla entre 11am y 3pm."
        )
    if temperature <= 12:
        return (
            "Hace frío: si tu mascota es de pelo corto, considera un abrigo "
            "para los paseos de la mañana y la noche."
        )
    if condition == "despejado":
        return (
            "Día soleado y templado: buen momento para un paseo largo, pero "
            "lleva agua igual."
        )
    return "Clima estable hoy: buen día para la rutina normal de paseo y juego."


def _fetch_from_open_meteo(lat: float, lon: float) -> dict:
    params = f"latitude={lat}&longitude={lon}&current=temperature_2m,weather_code&timezone=auto"
    url = f"{OPEN_METEO_URL}?{params}"
    with urllib.request.urlopen(url, timeout=REQUEST_TIMEOUT_SECONDS) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    current = payload["current"]
    return {
        "temperature": current["temperature_2m"],
        "weather_code": current["weather_code"],
    }


def get_weather_tip(lat: float = DEFAULT_LAT, lon: float = DEFAULT_LON, city: str = DEFAULT_CITY) -> dict:
    """Devuelve el consejo del dia. Nunca lanza: si la API externa falla o
    tarda, responde un tip generico con available=False para que el
    frontend pueda mostrarlo igual (degradacion controlada) o simplemente
    ocultar la tarjeta.
    """
    now = time.time()
    cached = _cache["data"]
    if cached is not None and (now - _cache["fetched_at"]) < CACHE_TTL_SECONDS:
        return cached

    try:
        raw = _fetch_from_open_meteo(lat, lon)
        condition = _condition_label(raw["weather_code"])
        result = {
            "available": True,
            "city": city,
            "temperature": round(raw["temperature"], 1),
            "condition": condition,
            "tip": _build_tip(raw["temperature"], condition),
            "source": "open-meteo.com",
        }
    except (URLError, TimeoutError, KeyError, ValueError, OSError):
        result = {
            "available": False,
            "city": city,
            "temperature": None,
            "condition": None,
            "tip": "Recuerda siempre tener agua fresca disponible para tu mascota.",
            "source": None,
        }

    _cache["data"] = result
    _cache["fetched_at"] = now
    return result
