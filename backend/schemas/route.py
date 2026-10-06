from enum import Enum
from typing import List

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class RoutingStrategy(str, Enum):
    WEIGHTED = "weighted"
    PRIORITY = "priority"
    LEAST_LOAD = "least_load"
    LATENCY = "latency"


class BackendCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    url: HttpUrl
    weight: int = Field(default=1, gt=0)
    priority: int = Field(default=1, gt=0)


class RouteCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    path: str = Field(min_length=1, max_length=255)
    strategy: RoutingStrategy
    backends: List[BackendCreate] = Field(min_length=1)


class BackendResponse(BaseModel):
    id: int
    name: str
    url: str
    weight: int
    priority: int
    active_connections: int
    latency_ms: float
    healthy: bool

    model_config = ConfigDict(from_attributes=True)


class RouteResponse(BaseModel):
    id: int
    name: str
    path: str
    strategy: RoutingStrategy
    backends: List[BackendResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)