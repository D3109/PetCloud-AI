from fastapi import FastAPI

from app.api import auth, users

app = FastAPI(title="PetCloud IA")

app.include_router(users.router)
app.include_router(auth.router)


@app.get("/api/v1/health")
def health():
    return {"status": "ok"}
