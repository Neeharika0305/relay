from app.database import Base, engine

from app.models import Project
from app.models import Route
from app.models import Backend
from app.models import RoutingRule


def init_db():
    Base.metadata.create_all(bind=engine)

    from sqlalchemy.orm import Session

    with Session(engine) as db:
        project = db.query(Project).filter(Project.id == 1).first()

        if project is None:
            project = Project(
                name="Relay Default Project",
                api_key="relay-default-api-key",
            )

            db.add(project)
            db.commit()