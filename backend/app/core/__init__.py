"""
Capa core (infraestructura transversal)
=======================================

Cuarta capa del backend, usada por las otras tres:

    api  ->  services  ->  models  ->  core

No es un paso mas del flujo de una peticion, sino la base que las demas
capas comparten:
  - config.py    -> variables de entorno / configuracion (Settings).
  - database.py  -> motor de SQLAlchemy y la sesion de base de datos
                     (get_db, usada por toda la capa de API).
  - security.py  -> hashing de contrasenas, creacion/lectura de JWT.
  - deps.py      -> dependencias de FastAPI para autenticacion y
                     permisos por rol (las que protegen cada endpoint
                     de app/api, p. ej. "solo admin", "solo logueado").

Nada en esta capa sabe de productos, pedidos ni ningun otro dominio de
negocio: es infraestructura generica que cualquier parte del backend
puede importar.
"""
