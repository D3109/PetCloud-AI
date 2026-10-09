"""Proteccion simple contra fuerza bruta en el login.

Lleva la cuenta de intentos fallidos recientes por correo (normalizado
a minusculas) en memoria del proceso. No persiste entre reinicios del
servidor ni se comparte entre varios procesos/workers, pero es
suficiente para este proyecto (un solo proceso de desarrollo) y evita
que alguien pruebe miles de contraseñas seguidas contra una cuenta.

No se usa la IP como clave porque en un entorno de desarrollo /
Codespaces todas las peticiones suelen llegar con la misma IP interna,
lo que bloquearia a todos los usuarios a la vez; el correo es una
clave mas util para este caso.
"""
import time
from collections import defaultdict

MAX_ATTEMPTS = 5
WINDOW_SECONDS = 15 * 60  # 15 minutos

_failed_attempts: dict[str, list[float]] = defaultdict(list)


def _prune(key: str) -> list[float]:
    now = time.time()
    attempts = [t for t in _failed_attempts.get(key, []) if now - t < WINDOW_SECONDS]
    _failed_attempts[key] = attempts
    return attempts


def is_locked(key: str) -> bool:
    return len(_prune(key.lower())) >= MAX_ATTEMPTS


def register_failure(key: str) -> None:
    key = key.lower()
    attempts = _prune(key)
    attempts.append(time.time())
    _failed_attempts[key] = attempts


def clear(key: str) -> None:
    _failed_attempts.pop(key.lower(), None)
