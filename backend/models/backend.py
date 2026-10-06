from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Backend(Base):
    __tablename__ = "backends"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    route_id: Mapped[int] = mapped_column(
        ForeignKey("routes.id", ondelete="CASCADE"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    weight: Mapped[int] = mapped_column(
        Integer,
        default=1,
    )

    priority: Mapped[int] = mapped_column(
        Integer,
        default=1,
    )

    active_connections: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    latency_ms: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    healthy: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    route = relationship(
        "Route",
        back_populates="backends",
    )