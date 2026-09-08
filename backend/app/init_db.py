from app.database import Base, engine
from app.models import (
    Backend,
    Project,
    Route,
    RoutingRule,
)


def init_db():
    Base.metadata.create_all(bind=engine)