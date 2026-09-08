# Relay

> A globally scalable intelligent URL routing and reliability platform designed to route traffic across backend services based on health, performance, and routing policies.

Relay is an infrastructure-focused platform that goes beyond traditional URL shortening by combining **URL routing, backend health monitoring, intelligent traffic distribution, caching, reliability mechanisms, and observability**.

The goal is to build a production-oriented routing system capable of making intelligent decisions about where incoming requests should be sent.

---

## 🚀 Overview

Traditional URL shorteners primarily map a short URL to a destination.

Relay focuses on the infrastructure behind the request.

When a request reaches Relay, the platform can evaluate:

- Backend health
- Routing rules
- Service availability
- Request distribution
- Cached routing information
- Backend failures
- Traffic policies
- Performance metrics

and determine the most appropriate backend destination.

### Core Flow

```text
                        ┌──────────────────┐
                        │      Client      │
                        └────────┬─────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │  Relay Router    │
                        └────────┬─────────┘
                                 │
                 ┌───────────────┼───────────────┐
                 │               │               │
                 ▼               ▼               ▼
          Routing Rules      Redis Cache    Health Checks
                 │               │               │
                 └───────────────┼───────────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │ Backend Services │
                        └────────┬─────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │  Observability   │
                        │ Prometheus +     │
                        │ Grafana          │
                        └──────────────────┘
