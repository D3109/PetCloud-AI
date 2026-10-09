from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    ai,
    audit,
    auth,
    cart,
    categories,
    dashboard,
    inventory,
    orders,
    payments,
    pets,
    products,
    promotions,
    reports,
    surveys,
    users,
)

app = FastAPI(title="PetCloud IA")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # allow_credentials=False porque la autenticacion es con un Bearer
    # token en el header Authorization (nunca con cookies), por lo que
    # no se necesitan credenciales de navegador. Combinar
    # allow_origins=["*"] con allow_credentials=True permitiria que
    # cualquier sitio hiciera solicitudes "con credenciales" contra la
    # API, asi que se deja explicitamente desactivado.
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(inventory.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(promotions.router)
app.include_router(payments.router)
app.include_router(ai.router)
app.include_router(pets.router)
app.include_router(surveys.router)
app.include_router(audit.router)
app.include_router(dashboard.router)
app.include_router(reports.router)


@app.get("/api/v1/health")
def health():
    return {"status": "ok"}
