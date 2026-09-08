from fastapi import FastAPI
from sqlalchemy import text

from app.config import settings
from app.database import engine
from app.init_db import init_db
from app.redis_client import redis_client


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0"
)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def root():
    return {
        "service": "Relay",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
def health():
    database_status = "ok"
    redis_status = "ok"

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        database_status = "error"

    try:
        redis_client.ping()
    except Exception:
        redis_status = "error"

    overall_status = (
        "ok"
        if database_status == "ok" and redis_status == "ok"
        else "degraded"
    )

    return {
        "status": overall_status,
        "database": database_status,
        "redis": redis_status
    }