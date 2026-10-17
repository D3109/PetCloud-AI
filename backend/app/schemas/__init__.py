"""
Capa de schemas (contrato HTTP de entrada/salida)
=======================================

No es una de las 4 capas de flujo principal (api -> services -> models
-> core), sino el "idioma" que usa la capa de API para hablar con el
mundo exterior: cada archivo define clases de Pydantic que describen
que forma tiene el JSON que un endpoint espera recibir (ProductCreate,
UserLogin...) y que forma tiene el JSON que devuelve (ProductOut,
OrderOut...).

Por que existen separados de app/models:
  - app/models describe como se guardan los datos en la base de datos.
  - app/schemas describe que ve el cliente HTTP: puede ocultar campos
    sensibles (p. ej. el hash de la contrasena), renombrar campos, o
    combinar datos de varias tablas en una sola respuesta.
  - Esta separacion es lo que permite validar automaticamente cada
    request (FastAPI rechaza un body que no cumpla el schema) y generar
    la documentacion interactiva de la API (/docs) sin trabajo extra.
"""
