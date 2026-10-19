# Arquitectura de PetCloud IA

Arquitectura **cliente-servidor en capas (N-capas), de tipo monolito
modular**: el frontend está totalmente desacoplado del backend (solo se
comunican por HTTP/REST) y el backend está organizado en 4 capas internas
con responsabilidades separadas. No es microservicios: un único proceso
FastAPI sirve toda la API.

```
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND  (frontend/)                                       │
│  HTML/CSS/JS "vanilla" multi-página, servido como archivos   │
│  estáticos. No depende de ningún framework ni bundler.       │
└───────────────────────────┬────────────────────────────────┘
                             │  HTTP / JSON (fetch)
┌───────────────────────────▼────────────────────────────────┐
│  BACKEND  (backend/app/) — 4 capas, de afuera hacia adentro  │
│                                                                │
│  1. api/        Endpoints REST (FastAPI routers)             │
│        │        valida con schemas/, exige permisos          │
│        ▼        (core/deps.py), llama a services/             │
│  2. services/   Lógica de negocio (reglas, orquestación)      │
│        │        usa models/ para leer y escribir              │
│        ▼                                                      │
│  3. models/     ORM (SQLAlchemy) — estructura de las tablas   │
│        │                                                      │
│        ▼                                                      │
│     PostgreSQL                                                │
│                                                                │
│  schemas/  (transversal)  — contrato JSON de entrada/salida   │
│  core/     (transversal)  — config, DB engine, seguridad,     │
│                              JWT, dependencias de permisos     │
└────────────────────────────────────────────────────────────┘
```

## Cómo "ver" las capas en el código

Cada carpeta de `backend/app/` tiene ahora su propio `__init__.py` con un
docstring explicando esa capa — ábrelo en el editor y aparece arriba de
todo el archivo, sin tener que leer este documento:

| Carpeta | Capa | Qué contiene |
|---|---|---|
| `backend/app/api/` | 1. Presentación | 18 routers (`products.py`, `orders.py`, `auth.py`, `weather.py`...), uno por dominio. Endpoints REST. |
| `backend/app/schemas/` | — (contrato) | Clases Pydantic: forma del JSON que entra y sale de cada endpoint. |
| `backend/app/services/` | 2. Negocio | Reglas de negocio reales, una por dominio (`product_service.py`...). |
| `backend/app/models/` | 3. Persistencia | Clases SQLAlchemy = tablas de PostgreSQL. |
| `backend/app/core/` | 4. Infraestructura | `config.py`, `database.py`, `security.py`, `deps.py`, `rate_limit.py`. |
| `backend/app/main.py` | — (arranque) | Crea la app de FastAPI y registra los 17 routers de `api/`. |
| `backend/database/migrations/` | — (versionado de esquema) | Migraciones de Alembic (cambios de estructura de tablas). |

Regla simple para ubicar cualquier cambio:
- ¿Es una ruta nueva o cambia qué devuelve un endpoint? → `api/` (+ `schemas/` si cambia el JSON).
- ¿Es una regla de negocio ("no permitir X si Y")? → `services/`.
- ¿Es un campo nuevo en una tabla? → `models/` + una migración en `database/migrations/versions/`.
- ¿Es configuración, autenticación o algo que usan todas las capas? → `core/`.

## Integraciones con APIs externas

| Qué | Capa / archivo | Para qué |
|---|---|---|
| IA generativa (Gemini) | `services/ai_client.py` + `services/ai_service.py` | Chat de recomendaciones ("Pet-IA") |
| Clima (Open-Meteo, sin API key) | `services/weather_tip_service.py` + `api/weather.py` | Tarjeta "Consejo del día" en la portada. Documentada en detalle en [docs/api_clima_mascotas.md](./docs/api_clima_mascotas.md) (cómo se aplicó, pros/contras y mitigaciones). |

## Frontend

```
frontend/
├── *.html          10 páginas (index, admin, cart, login, profile...)
├── css/styles.css  Un único stylesheet, con variables de marca en :root
└── js/
    ├── config.js, api.js   Base de la API + helper de fetch autenticado
    ├── nav.js, footer.js, chat.js   Inyectados en todas las páginas
    └── catalog.js, cart.js, admin.js, ...   Un archivo por página/módulo
```

No hay un framework de frontend: cada página es HTML independiente que
carga los mismos scripts compartidos (nav, footer, chat) más el script
propio de esa página.
