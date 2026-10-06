from sqlalchemy.orm import Session

from app.models import Backend
from health.health_checker import check_backend_health


async def run_health_checks(db: Session) -> None:
    backends = (
        db.query(Backend)
        .filter(Backend.enabled.is_(True))
        .all()
    )

    for backend in backends:
        healthy = await check_backend_health(backend.url)

        if not healthy:
            backend.enabled = False
            print(
                f"[Relay Health] UNHEALTHY: "
                f"{backend.url} -> disabled"
            )

        else:
            print(
                f"[Relay Health] HEALTHY: "
                f"{backend.url}"
            )

    db.commit()
