"""
Capa API (presentacion / entrada HTTP)
=======================================

Esta carpeta es la primera de las 4 capas del backend:

    api  ->  services  ->  models  ->  core

Cada archivo de aqui (products.py, orders.py, auth.py, etc.) define un
APIRouter de FastAPI: los endpoints REST que expone la aplicacion
(decide rutas, metodos HTTP, codigos de estado, y que rol puede llamar
cada endpoint via las dependencias de app/core/deps.py).

Reglas de esta capa:
  - SI puede: validar el request con un schema de Pydantic (app/schemas),
    revisar permisos/autenticacion, y llamar a una funcion de la capa de
    servicios (app/services) para hacer el trabajo real.
  - NO debe: escribir consultas SQL/ORM directamente, ni contener reglas
    de negocio (eso vive en app/services). Un router delgado es mas facil
    de leer y de testear.

Los 14 routers de esta capa se registran todos en app/main.py.
"""
