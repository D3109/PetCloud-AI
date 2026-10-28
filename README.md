# PetCloud-AI

Plataforma de comercio electrónico para una tienda de mascotas, con un
módulo de gestión de servicios de TI integrado (catálogo, incidentes, KPIs
y auditoría). Backend en FastAPI (Python) y frontend en HTML/CSS/JS sin
framework.

Ver [ARCHITECTURE.md](./ARCHITECTURE.md) para el mapa de la arquitectura
(capas del backend, estructura del frontend y dónde ubicar cada tipo de
cambio).

## Requisitos

- Python 3.11+
- Docker (para levantar PostgreSQL) o un PostgreSQL 16 ya accesible
- No se necesita Node: el frontend es HTML/CSS/JS plano, sin build

## 1. Base de datos

```bash
docker compose up -d
```

Levanta PostgreSQL 16 en el puerto `5432` (usuario `petcloud`, contraseña
`petcloud`, base `petcloud_ia`), definido en `docker-compose.yml`.

## 2. Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

cp ../.env.example ../.env   # completar con tus valores, ver abajo

alembic upgrade head                                  # aplica las migraciones
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API en `http://localhost:8000`, documentación interactiva (Swagger) en
`http://localhost:8000/docs`.

Si usás el devcontainer (`.devcontainer/devcontainer.json`), las
dependencias de `backend/requirements.txt` se instalan solas al crear el
contenedor.

### Datos iniciales (opcional)

```bash
cd backend
python3 scripts/create_root.py     # crea el usuario ROOT / superadministrador
python3 scripts/seed_products.py   # carga categorías y productos de ejemplo
```

## 3. Frontend

```bash
cd frontend
python -m http.server 5500
```

Abrir `http://localhost:5500`. `frontend/js/config.js` detecta sola la URL
del backend: usa `http://localhost:8000` en local, y en GitHub Codespaces
arma la URL del puerto 8000 a partir del hostname del puerto donde corre
el frontend.

## Variables de entorno (`.env` en la raíz del repo)

| Variable | Obligatoria | Qué es |
| --- | --- | --- |
| `DATABASE_URL` | Sí | Cadena de conexión a PostgreSQL (`postgresql://user:password@host:5432/db`) |
| `JWT_SECRET_KEY` | Sí | Clave para firmar los tokens JWT |
| `GOOGLE_API_KEY` | Sí | API key de Google Gemini (asistente de compras con IA) |
| `JWT_ALGORITHM` | No (`HS256`) | Algoritmo de firma del JWT |
| `JWT_EXPIRE_MINUTES` | No (`60`) | Minutos de expiración del token |
| `AI_MODEL` | No (`gemini-3.8-flash`) | Modelo de Gemini usado por el asistente |
| `GOOGLE_OAUTH_CLIENT_ID` | No | Client ID de Google para "Ingresar con Google" |
| `FRONTEND_BASE_URL` | No | URL pública del frontend, para el enlace de restablecer contraseña en el correo |
| `SMTP_HOST` / `SMTP_PORT` / `SMTP_USER` / `SMTP_PASSWORD` / `SMTP_FROM` / `SMTP_USE_TLS` | No | Envío de correos transaccionales (confirmación de pago, recuperación de contraseña) |

Sin SMTP configurado, el correo de recuperación de contraseña no se envía,
pero el token sigue siendo válido para pegarlo a mano en la página de
restablecer contraseña.

