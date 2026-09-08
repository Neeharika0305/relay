from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String

from app.database import Base


class Backend(Base):
    __tablename__ = "backends"

    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False)

    url = Column(String(500), nullable=False)
    region = Column(String(100), nullable=False)

    weight = Column(Float, default=1.0)
    priority = Column(Integer, default=1)

    enabled = Column(Boolean, default=True)