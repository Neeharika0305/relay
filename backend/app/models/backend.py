from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String

from app.database import Base


class Backend(Base):
    __tablename__ = "backends"

    id = Column(Integer, primary_key=True, index=True)

    route_id = Column(
        Integer,
        ForeignKey("routes.id", ondelete="CASCADE"),
        nullable=False,
    )

    url = Column(String(500), nullable=False)

    weight = Column(Float, nullable=False, default=1.0)

    priority = Column(Integer, nullable=False, default=1)

    enabled = Column(Boolean, nullable=False, default=True)