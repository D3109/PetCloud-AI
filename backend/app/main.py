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
    products,
    promotions,
    surveys,
    users,
)

app = FastAPI(title="PetCloud IA")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
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
app.include_router(surveys.router)
app.include_router(audit.router)
app.include_router(dashboard.router)


@app.get("/api/v1/health")
def health():
    return {"status": "ok"}
