from fastapi import FastAPI
from app.routes.jobs import router as jobs_router
from app.db import init_db

app = FastAPI(title="Dubber AI", version="0.1.0")


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(jobs_router)