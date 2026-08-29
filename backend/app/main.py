from fastapi import FastAPI

app = FastAPI(title="PetCloud IA")


@app.get("/api/v1/health")
def health():
    return {"status": "ok"}