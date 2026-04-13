from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Alert, AlertSeverity

THRESHOLDS: dict[str, list[tuple[float, AlertSeverity]]] = {
    "cpu_usage":    [(95.0, AlertSeverity.CRITICAL), (80.0, AlertSeverity.WARNING)],
    "memory_usage": [(90.0, AlertSeverity.CRITICAL), (75.0, AlertSeverity.WARNING)],
    "temperature":  [(85.0, AlertSeverity.CRITICAL), (70.0, AlertSeverity.WARNING)],
    "disk_usage":   [(95.0, AlertSeverity.CRITICAL), (80.0, AlertSeverity.WARNING)],
}


async def evaluate_and_create_alert(
    db: AsyncSession,
    device_id: int,
    key: str,
    value: float
) -> Alert | None:
    if key not in THRESHOLDS:
        return None

    for threshold, severity in THRESHOLDS[key]:
        if value >= threshold:
            alert = Alert(
                device_id=device_id,
                severity=severity,
                message=f"{key} is {value} (threshold: {threshold})"
            )
            db.add(alert)
            await db.commit()
            await db.refresh(alert)
            return alert

    return None
