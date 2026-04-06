from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Device, Metric
from app.schemas import MetricCreate, MetricResponse
from app.services.alert_service import evaluate_and_create_alert

router = APIRouter(prefix="/devices", tags=["metrics"])

@router.post("/{device_id}/metrics", response_model=MetricResponse, status_code=201)
async def create_metric(
    device_id: int,
    payload: MetricCreate,
    db: AsyncSession = Depends(get_db)
):
    device = await db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    existing = await db.execute(
        select(Metric).where(
            (Metric.device_id == device_id) & 
            (Metric.key == payload.key)
        )
    )
    if existing.scalars().first():
        raise HTTPException(status_code=409, detail="Metric already exists")

    metric = Metric(device_id=device_id, **payload.model_dump())
    db.add(metric)
    await db.commit()
    await db.refresh(metric)

    await evaluate_and_create_alert(db, device_id, payload.key, payload.value)

    return metric

@router.get("/{device_id}/metrics", response_model=list[MetricResponse])
async def list_metrics(device_id: int, db: AsyncSession = Depends(get_db)):
    device = await db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    result = await db.execute(
        select(Metric).where(Metric.device_id == device_id)
    )
    return result.scalars().all()