from sqlalchemy import Column, ForeignKey, Integer, String

from app.database import Base


class RoutingRule(Base):
    __tablename__ = "routing_rules"

    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False)

    rule_type = Column(String(50), nullable=False)
    rule_value = Column(String(255), nullable=False)
    priority = Column(Integer, default=1)