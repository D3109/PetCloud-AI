"""
Capa de modelos (persistencia / ORM)
=======================================

Tercera de las 4 capas del backend:

    api  ->  services  ->  models  ->  core

Cada archivo de aqui es una clase de SQLAlchemy que representa una
tabla de PostgreSQL (product.py -> tabla "products", order.py -> tabla
"orders", etc.), con sus columnas, tipos y relaciones (ForeignKey,
relationship) con otras tablas.

Reglas de esta capa:
  - Describe la ESTRUCTURA de los datos, no el comportamiento de
    negocio (eso vive en app/services) ni el formato que ve el
    cliente HTTP (eso vive en app/schemas).
  - Los cambios de estructura (agregar una columna, una tabla nueva)
    se acompanan de una migracion de Alembic en
    backend/database/migrations/versions/.
"""
