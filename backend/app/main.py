from fastapi import FastAPI
from sqlalchemy import text

from app.config import settings
from app.database import engine
from app.redis_client import redis_client
from app.init_db import init_db

from routes.routes import router as routes_router
from routes.proxy import router as proxy_router

from health.health_loop import health_check_loop
import asyncio


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
)


@app.on_event("startup")
def startup():
    init_db()
    asyncio.create_task(health_check_loop())


@app.get("/")
def root():
    return {
        "service": "Relay",
        "status": "running",
        "version": "1.0.0",
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
        "redis": redis_status,
    }


app.include_router(routes_router)
app.include_router(proxy_router)
