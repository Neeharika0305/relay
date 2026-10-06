import asyncio

from app.database import SessionLocal
from health.health_manager import run_health_checks


async def health_check_loop(interval: int = 10) -> None:
    while True:
        db = SessionLocal()

        try:
            await run_health_checks(db)
        except Exception as exc:
            print(f"[Relay Health] ERROR: {exc}")
        finally:
            db.close()

        await asyncio.sleep(interval)
