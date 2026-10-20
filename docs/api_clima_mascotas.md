# API "Consejo del día" (clima + cuidado de mascotas)

Documentación de la integración con una API externa, agregada como función
"plus" del catálogo: una tarjeta en la portada con un consejo de cuidado
de la mascota según el clima real del día.

## 0. Arquitectura general en capas del proyecto (contexto)

PetCloud IA usa una arquitectura **cliente-servidor en capas (N-capas),
tipo monolito modular**: el frontend y el backend están totalmente
desacoplados (solo se comunican por HTTP/JSON) y el backend está
organizado en 4 capas internas con responsabilidades separadas. No es
microservicios: un único proceso de FastAPI sirve toda la API.

```
Petición HTTP (del frontend)
        │
        ▼
1. API (presentación)       → backend/app/api/
        │   valida la entrada, exige permisos
        ▼
2. Servicios (negocio)       → backend/app/services/
        │   reglas de negocio, decide qué hacer
        ▼
3. Modelos (persistencia)    → backend/app/models/
        │   estructura de las tablas (ORM)
        ▼
   PostgreSQL (la base de datos real)
```

Transversales a esas 3 capas (las usan todas, no son un escalón más):
- **`backend/app/schemas/`** — forma del JSON de entrada/salida de cada endpoint.
- **`backend/app/core/`** — configuración, conexión a la base de datos, seguridad/JWT, permisos.

| Capa | Carpeta | Ejemplos de archivos |
|---|---|---|
| 1. API (presentación) | `backend/app/api/` | `products.py`, `orders.py`, `auth.py`, `cart.py`, `weather.py`... (18 routers, uno por dominio) |
| 2. Servicios (negocio) | `backend/app/services/` | `product_service.py`, `order_service.py`, `cart_service.py`, `weather_tip_service.py` |
| 3. Modelos (persistencia) | `backend/app/models/` | `product.py` → tabla `products`, `user.py` → tabla `users`, `order.py` → tabla `orders` |
| — Base de datos | *(fuera del código)* | PostgreSQL; estructura versionada con migraciones en `backend/database/migrations/versions/` |
| Transversal (contrato) | `backend/app/schemas/` | `product.py`, `weather.py`... |
| Transversal (infraestructura) | `backend/app/core/` | `config.py`, `database.py`, `security.py`, `deps.py` |
| Arranque | `backend/app/main.py` | Crea la app de FastAPI y registra todos los routers de `api/` |

Regla simple para ubicar cualquier cambio:
- ¿Es una ruta nueva o cambia qué devuelve un endpoint? → `api/` (+ `schemas/` si cambia el JSON).
- ¿Es una regla de negocio ("no permitir X si Y")? → `services/`.
- ¿Es un campo nuevo en una tabla? → `models/` + una migración.
- ¿Es configuración, autenticación o algo que usan todas las capas? → `core/`.

**Frontend** (sin capas de negocio, sin framework — HTML/CSS/JS "vanilla"):

```
frontend/
├── *.html          10 páginas (index, admin, cart, login...)
├── css/styles.css  Un único stylesheet
└── js/
    ├── config.js, api.js   Base de la API + helper de fetch
    ├── nav.js, footer.js, chat.js   Se cargan en todas las páginas
    └── catalog.js, cart.js, admin.js...   Uno por página/módulo
```

El detalle completo de esta arquitectura general (con el diagrama ASCII
íntegro) vive en [`ARCHITECTURE.md`](../ARCHITECTURE.md), en la raíz del
repositorio. El resto de este documento se enfoca específicamente en la
API del clima.

## 1. Cómo se aplicó

Se integró contra **Open-Meteo** (`https://api.open-meteo.com`), una API
pública y gratuita de pronóstico del clima que no requiere API key ni
registro. La implementación sigue las 4 capas del backend:

```
GET /index.html
      │
      ▼
frontend/js/weather-tip.js  ──fetch──▶  GET /api/v1/weather-tip
                                               │
                                               ▼
                                 backend/app/api/weather.py        (capa 1: API)
                                               │
                                               ▼
                         backend/app/services/weather_tip_service.py  (capa 2: servicios)
                                               │
                                               ▼
                              api.open-meteo.com (servicio externo)
```

- **`backend/app/services/weather_tip_service.py`**: llama a Open-Meteo con
  la latitud/longitud de Bogotá (ciudad base de la tienda), recibe
  temperatura actual + código de clima (WMO), y los traduce a un consejo
  de cuidado en español ("hace calor: agua fresca", "va a llover: paseo
  corto y secar las patas", etc). Usa `urllib` de la librería estándar de
  Python (no se agregó ninguna dependencia nueva).
- **`backend/app/schemas/weather.py`**: forma del JSON de salida
  (`WeatherTipOut`).
- **`backend/app/api/weather.py`**: endpoint público `GET /api/v1/weather-tip`
  (sin autenticación, porque se muestra a cualquier visitante, incluso sin
  iniciar sesión).
- **`frontend/js/weather-tip.js`** + `#weather-tip` en `index.html`:
  consulta el endpoint al cargar la portada y pinta la tarjeta bajo las
  categorías rápidas (Gatos/Perros/Juguetes).

No toca la base de datos ni los modelos: es la única capa del backend que
no pasa por `models/`, porque no persiste nada, solo consulta un servicio
externo y devuelve una recomendación calculada al vuelo.

## 2. Para qué se aplicó

Para darle al catálogo un valor agregado real más allá de listar
productos: una recomendación contextual y que cambia todos los días,
coherente con el mensaje de "Nuestra IA te recomienda qué comprar según tu
perro o gato" del hero. Es, además, un ejemplo concreto de integración con
una API externa de terceros dentro del proyecto (más allá de la IA
generativa que ya usa `GOOGLE_API_KEY`), útil como plus a mostrar si el
proyecto se sustenta o evalúa.

## 3. Qué funcionalidad tiene

- Consulta la temperatura y condición climática actual (sol, nublado,
  niebla, lluvia, tormenta, nieve) de la ciudad configurada.
- Traduce esa condición en **un consejo de cuidado distinto según el
  caso** (frío, calor, lluvia, clima estable), no un mensaje genérico fijo.
- Cachea la respuesta en memoria **30 minutos**, así que no golpea la API
  externa en cada visita de cada usuario, solo una vez cada media hora.
- Si la API externa falla, tarda demasiado (timeout de 4s) o responde algo
  inesperado, el servicio **nunca lanza error**: responde un consejo
  genérico (`available: false`) sin mencionar clima, y el frontend lo
  muestra igual o lo oculta sin romper la página.

## 4. Qué contras puede tener y cómo se solucionan

| Contra | Cómo se mitiga |
|---|---|
| Depende de un servicio externo fuera de nuestro control (puede caerse o cambiar su API). | El `try/except` en `weather_tip_service.get_weather_tip()` captura cualquier falla de red o de formato y devuelve un consejo genérico de respaldo; la portada nunca se rompe ni muestra un error al usuario. |
| Latencia: cada llamada a Open-Meteo tarda cierto tiempo y podría hacer lenta la portada. | Cache en memoria de 30 minutos (`CACHE_TTL_SECONDS`): la mayoría de las visitas reciben la respuesta cacheada, no una llamada nueva. Además hay un timeout corto (4s) para no dejar la petición colgada. |
| Límite de uso (rate limit) de la API gratuita si el tráfico crece mucho. | El mismo cache de 30 minutos reduce drásticamente el número de llamadas reales (como mucho ~48 al día, sin importar cuántas visitas tenga la tienda). Si el proyecto crece mucho más, se puede mover a un cache compartido (Redis) en vez de uno en memoria por proceso. |
| Por ahora usa una ciudad fija (Bogotá) y no la ciudad real de cada usuario. | Es una limitación conocida y documentada en el propio código (`weather_tip_service.py`, comentario sobre `DEFAULT_CITY`): cuando el perfil de usuario guarde una ciudad, el servicio puede recibir esa latitud/longitud en vez de la fija, sin cambiar su diseño. |
| El endpoint es público (sin autenticación), lo que en teoría permite que cualquiera lo llame muchas veces. | Como está cacheado 30 minutos del lado del servidor, aunque lo llamen muchas veces seguidas, solo se le pega a Open-Meteo una vez por ventana de 30 min; no hay forma de "agotar" la API externa desde afuera. |

## 5. Dónde está en el diagrama de capas

Ubicación exacta dentro de `ARCHITECTURE.md`:

- **Capa 1 (API / presentación)**: `backend/app/api/weather.py` — nuevo
  router, registrado en `app/main.py` junto a los demás (`app.include_router(weather.router)`).
- **Capa 2 (servicios / negocio)**: `backend/app/services/weather_tip_service.py`
  — aquí vive toda la lógica: la llamada HTTP externa, el cache, el
  mapeo clima → consejo y el manejo de errores.
- **Transversal (contrato)**: `backend/app/schemas/weather.py` — forma del
  JSON de salida (`WeatherTipOut`).
- **Capa 3 (modelos / persistencia)**: no aplica. Es la única
  funcionalidad del backend que no toca `models/` ni la base de datos,
  porque no guarda nada: calcula la respuesta en el momento.
- **Frontend**: `frontend/js/weather-tip.js` (un archivo nuevo, igual de
  independiente que `catalog.js` o `cart.js`) + el contenedor
  `#weather-tip` en `index.html` + sus estilos en `css/styles.css`.

También se agregó una fila a la tabla de capas de `ARCHITECTURE.md` para
que quede ahí documentado junto con el resto del backend.
