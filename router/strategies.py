from typing import List
import random

from .rules import Backend


def weighted_routing(backends: List[Backend]) -> Backend:
    healthy_backends = [
        backend for backend in backends
        if backend.healthy
    ]

    if not healthy_backends:
        raise RuntimeError("No healthy backends available")

    return random.choices(
        healthy_backends,
        weights=[backend.weight for backend in healthy_backends],
        k=1,
    )[0]


def priority_routing(backends: List[Backend]) -> Backend:
    healthy_backends = [
        backend for backend in backends
        if backend.healthy
    ]

    if not healthy_backends:
        raise RuntimeError("No healthy backends available")

    return min(
        healthy_backends,
        key=lambda backend: backend.priority
    )


def least_load_routing(backends: List[Backend]) -> Backend:
    healthy_backends = [
        backend for backend in backends
        if backend.healthy
    ]

    if not healthy_backends:
        raise RuntimeError("No healthy backends available")

    return min(
        healthy_backends,
        key=lambda backend: backend.active_connections
    )


def latency_routing(backends: List[Backend]) -> Backend:
    healthy_backends = [
        backend for backend in backends
        if backend.healthy
    ]

    if not healthy_backends:
        raise RuntimeError("No healthy backends available")

    return min(
        healthy_backends,
        key=lambda backend: backend.latency_ms
    )