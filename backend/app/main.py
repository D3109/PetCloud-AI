from fastapi import FastAPI

from app.api import ai, auth, categories, inventory, products, users

app = FastAPI(title="PetCloud IA")

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(inventory.router)
app.include_router(ai.router)


@app.get("/api/v1/health")
def health():
    return {"status": "ok"}
