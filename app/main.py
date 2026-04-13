from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import engine, Base
from app.routers import devices, metrics, alerts


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title="Device Management API",
    description="REST API for managing and monitoring infrastructure devices",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(devices.router)
app.include_router(metrics.router)
app.include_router(alerts.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
