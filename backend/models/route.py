from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from app.database import Base


class Route(Base):
    __tablename__ = "routes"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    name = Column(
        String(100),
        nullable=False,
    )

    path = Column(
        String(255),
        nullable=False,
        unique=True,
    )

    strategy = Column(
        String(50),
        nullable=False,
        default="weighted",
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
    )