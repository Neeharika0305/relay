from sqlalchemy.orm import Session

from app.models import Backend
from health.health_checker import check_backend_health


async def run_health_checks(db: Session) -> None:
    backends = (
        db.query(Backend)
        .filter(Backend.enabled.is_(True))
        .all()
    )

    # Also check previously disabled backends so they can recover.
    disabled_backends = (
        db.query(Backend)
        .filter(Backend.enabled.is_(False))
        .all()
    )

    all_backends = {
        backend.id: backend
        for backend in backends + disabled_backends
    }

    for backend in all_backends.values():
        healthy = await check_backend_health(backend.url)

        if healthy:
            if not backend.enabled:
                backend.enabled = True
                print(
                    f"[Relay Health] RECOVERED: "
                    f"{backend.url} -> enabled"
                )
            else:
                print(
                    f"[Relay Health] HEALTHY: "
                    f"{backend.url}"
                )

        else:
            if backend.enabled:
                backend.enabled = False
                print(
                    f"[Relay Health] UNHEALTHY: "
                    f"{backend.url} -> disabled"
                )
            else:
                print(
                    f"[Relay Health] STILL UNHEALTHY: "
                    f"{backend.url}"
                )

    db.commit()
