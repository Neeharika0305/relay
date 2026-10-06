from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum
from threading import Lock


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreaker:
    failure_threshold: int = 3
    recovery_timeout: float = 10.0

    def __post_init__(self):
        if self.failure_threshold <= 0:
            raise ValueError("failure_threshold must be greater than 0")

        if self.recovery_timeout <= 0:
            raise ValueError("recovery_timeout must be greater than 0")

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time: float | None = None
        self._lock = Lock()

    def allow_request(self) -> bool:
        with self._lock:
            if self.state == CircuitState.CLOSED:
                return True

            if self.state == CircuitState.OPEN:
                if self.last_failure_time is None:
                    return False

                elapsed = time.monotonic() - self.last_failure_time

                if elapsed >= self.recovery_timeout:
                    self.state = CircuitState.HALF_OPEN
                    return True

                return False

            # HALF_OPEN allows exactly one trial request.
            self.state = CircuitState.OPEN
            return False

    def record_success(self) -> None:
        with self._lock:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.last_failure_time = None

    def record_failure(self) -> None:
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.monotonic()

            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN

    def reset(self) -> None:
        with self._lock:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.last_failure_time = None
