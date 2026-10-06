from typing import Sequence
import random

from app.router.rules import Backend


class RoutingEngine:
    SUPPORTED_STRATEGIES = {
        "weighted",
        "priority",
        "least_load",
        "latency",
    }

    def select_backend(
        self,
        backends: Sequence[Backend],
        strategy: str = "weighted",
    ) -> Backend:
        if not backends:
            raise RuntimeError("No backends configured")

        healthy_backends = [
            backend
            for backend in backends
            if backend.healthy
        ]

        if not healthy_backends:
            raise RuntimeError("No healthy backends available")

        strategy = strategy.lower()

        if strategy not in self.SUPPORTED_STRATEGIES:
            raise ValueError(
                f"Unsupported routing strategy: {strategy}"
            )

        if strategy == "weighted":
            return self._weighted(healthy_backends)

        if strategy == "priority":
            return self._priority(healthy_backends)

        if strategy == "least_load":
            return self._least_load(healthy_backends)

        if strategy == "latency":
            return self._latency(healthy_backends)

        raise ValueError(
            f"Unsupported routing strategy: {strategy}"
        )

    @staticmethod
    def _weighted(backends: Sequence[Backend]) -> Backend:
        total_weight = sum(
            backend.weight
            for backend in backends
        )

        target = random.uniform(0, total_weight)
        cumulative = 0.0

        for backend in backends:
            cumulative += backend.weight

            if target <= cumulative:
                return backend

        return backends[-1]

    @staticmethod
    def _priority(backends: Sequence[Backend]) -> Backend:
        return min(
            backends,
            key=lambda backend: backend.priority,
        )

    @staticmethod
    def _least_load(backends: Sequence[Backend]) -> Backend:
        return min(
            backends,
            key=lambda backend: (
                backend.active_connections,
                backend.latency_ms,
            ),
        )

    @staticmethod
    def _latency(backends: Sequence[Backend]) -> Backend:
        return min(
            backends,
            key=lambda backend: (
                backend.latency_ms
                if backend.latency_ms > 0
                else float("inf"),
                backend.active_connections,
            ),
        )
