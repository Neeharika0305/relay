from dataclasses import dataclass


@dataclass
class Backend:
    id: str
    url: str

    weight: int = 1
    priority: int = 1

    active_connections: int = 0
    latency_ms: float = 0.0

    healthy: bool = True

    def __post_init__(self):
        if not self.id:
            raise ValueError("Backend id cannot be empty")

        if not self.url.startswith(("http://", "https://")):
            raise ValueError("Backend URL must start with http:// or https://")

        if self.weight <= 0:
            raise ValueError("Backend weight must be greater than 0")

        if self.priority <= 0:
            raise ValueError("Backend priority must be greater than 0")

        if self.active_connections < 0:
            raise ValueError("Active connections cannot be negative")

        if self.latency_ms < 0:
            raise ValueError("Latency cannot be negative")