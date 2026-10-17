"""
Capa de servicios (logica de negocio)
=======================================

Segunda de las 4 capas del backend:

    api  ->  services  ->  models  ->  core

Aqui vive el "como" de cada operacion: las reglas de negocio reales
(p. ej. "no se puede bajar el stock de un producto por debajo de cero",
"un pedido pagado no se puede volver a pagar", "solo un admin puede
cambiar el rol de otro usuario"). Cada archivo agrupa los servicios de
un dominio (product_service.py, order_service.py, auth_service.py...).

Reglas de esta capa:
  - Recibe una sesion de base de datos (db: Session) y datos ya
    validados por la capa de API.
  - Orquesta uno o mas modelos de app/models para leer/escribir en la
    base de datos, y devuelve objetos de dominio (no respuestas HTTP:
    eso lo arma la capa de API con los schemas de app/schemas).
  - Es la capa que mas conviene testear de forma aislada, porque no
    depende de FastAPI ni de HTTP.
"""
