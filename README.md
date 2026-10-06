# Relay 🚦

### Globally Scalable Intelligent Traffic Routing & Reliability Platform

Relay is a **high-performance traffic routing and reliability platform** built with Python and FastAPI. It intelligently routes incoming requests across multiple backend services while continuously monitoring their health, detecting failures, and automatically recovering unhealthy instances.

The project focuses on real-world **distributed systems, backend engineering, fault tolerance, traffic management, observability, and reliability engineering** concepts.

---

## ✨ Why Relay?

Modern applications rarely depend on a single backend server. A production system needs to decide:

* Which backend should handle a request?
* What happens when a backend becomes unhealthy?
* How can traffic be distributed intelligently?
* How can repeated failures be isolated?
* How can a recovered backend automatically return to service?
* How can latency and active load influence routing decisions?

**Relay is built to solve these problems.**

---

## 🏗️ Architecture

```text
                         ┌─────────────────────┐
                         │      Client         │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    Relay API        │
                         │      FastAPI        │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┼────────────────┐
                    │               │                │
                    ▼               ▼                ▼
             ┌────────────┐  ┌────────────┐  ┌─────────────┐
             │  Routing   │  │ Reliability│  │   Proxy     │
             │   Engine   │  │  Layer     │  │   Layer     │
             └─────┬──────┘  └──────┬─────┘  └──────┬──────┘
                   │                │                │
                   ▼                ▼                ▼
             ┌────────────┐   ┌────────────┐   ┌────────────┐
             │ PostgreSQL │   │   Redis    │   │  Backends  │
             │   Config   │   │   Cache    │   │  Services  │
             └────────────┘   └────────────┘   └────────────┘
                                      ▲
                                      │
                              ┌───────┴────────┐
                              │ Health Monitor │
                              │ Async Workers  │
                              └────────────────┘
```

---

## 🚀 Key Features

### Intelligent Traffic Routing

Relay supports multiple routing strategies:

* **Weighted Routing** — distribute traffic according to configured weights
* **Priority Routing** — prefer higher-priority backends
* **Least-Load Routing** — route traffic toward backends with fewer active requests
* **Latency-Aware Routing** — prefer backends with lower observed latency

Routing decisions are made dynamically instead of relying on a single static backend.

---

### ❤️ Automated Health Monitoring

Relay continuously monitors backend services using asynchronous health checks.

When a backend becomes unhealthy:

```text
Healthy
   │
   ▼
Health Check Fails
   │
   ▼
Backend Disabled
   │
   ▼
Traffic Removed
```

When the backend recovers:

```text
Disabled
   │
   ▼
Health Check Succeeds
   │
   ▼
Backend Re-enabled
   │
   ▼
Traffic Restored
```

This allows Relay to automatically recover from transient backend failures.

---

### 🛡️ Circuit Breaker

Relay includes circuit-breaker protection to prevent repeated requests from continuously hitting a failing backend.

```text
             failures
                │
                ▼
        ┌──────────────┐
        │    CLOSED    │
        └──────┬───────┘
               │
          threshold
               │
               ▼
        ┌──────────────┐
        │     OPEN     │
        └──────┬───────┘
               │
        recovery timeout
               │
               ▼
        ┌──────────────┐
        │  HALF_OPEN   │
        └──────┬───────┘
          │           │
       success      failure
          │           │
          ▼           ▼
       CLOSED        OPEN
```

The circuit breaker prevents cascading failures by temporarily stopping traffic to repeatedly failing upstream services.

---

## ⚡ Runtime Load & Latency Tracking

Relay tracks runtime information such as:

* Active connections
* Request latency
* Backend availability
* Routing decisions
* Circuit-breaker state

This information enables more intelligent routing decisions, particularly for **least-load** and **latency-aware** strategies.

---

## 🗄️ Persistent Configuration

PostgreSQL acts as the persistent source of truth for Relay configuration.

The database stores information such as:

* Backend services
* Routes
* Routing strategy
* Backend weights
* Backend priority
* Backend enabled/disabled state

This separates configuration from application memory and allows routing configuration to survive application restarts.

---

## ⚡ Redis Integration

Redis is integrated for high-speed application data access and is designed to support future distributed coordination and caching capabilities.

The architecture allows Redis to become an important component for:

* Route caching
* Distributed state
* Rate limiting
* High-frequency configuration access

---

## 🔄 Request Flow

A typical request follows this path:

```text
Client
  │
  ▼
/v1/proxy/{route}
  │
  ▼
Load route configuration
  │
  ▼
Check available backends
  │
  ▼
Select backend using routing strategy
  │
  ▼
Circuit-breaker validation
  │
  ▼
Forward request
  │
  ▼
Track latency / active connections
  │
  ▼
Return response
```

---

## 🧪 Testing

Relay includes automated tests covering core backend functionality.

Current test suite:

```text
21 passed
```

Testing includes areas such as:

* Routing strategies
* Backend health management
* Automatic recovery
* Circuit-breaker behavior
* API endpoints
* Proxy behavior

Run the test suite with:

```bash
pytest
```

---

## 🛠️ Tech Stack

| Technology     | Purpose                     |
| -------------- | --------------------------- |
| **Python**     | Core backend                |
| **FastAPI**    | REST API                    |
| **PostgreSQL** | Persistent configuration    |
| **Redis**      | Caching / distributed state |
| **HTTPX**      | Async HTTP communication    |
| **SQLAlchemy** | Database access             |
| **Pytest**     | Automated testing           |
| **Docker**     | Containerization            |
| **Prometheus** | Metrics                     |
| **Grafana**    | Monitoring & visualization  |

---

## 📁 Project Structure

```text
relay/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── redis_client.py
│   │   │
│   │   ├── proxy/
│   │   ├── health/
│   │   └── reliability/
│   │
│   ├── requirements.txt
│   └── Dockerfile
│
├── router/
│   └── routing/
│       └── routing_engine.py
│
├── monitoring/
│   └── prometheus.yml
│
├── tests/
│
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## 🐳 Running with Docker

Clone the repository:

```bash
git clone https://github.com/Neeharika0305/relay.git
cd relay
```

Start the services:

```bash
docker compose up --build
```

Relay API:

```text
http://localhost:8000
```

Swagger API documentation:

```text
http://localhost:8000/docs
```

Prometheus:

```text
http://localhost:9090
```

Grafana:

```text
http://localhost:3000
```

---

## 🔌 API Examples

### Health

```http
GET /health
```

Example response:

```json
{
  "status": "ok"
}
```

### Routes

```http
GET /v1/routes
```

### Proxy Traffic

```http
GET /v1/proxy/{route}
```

Example:

```text
GET /v1/proxy/payments
```

Relay selects an appropriate healthy backend and forwards the request.

---

## 🎯 Engineering Concepts Demonstrated

Relay was designed as a practical backend/distributed-systems project rather than a CRUD application.

The project demonstrates:

* Traffic routing
* Load balancing
* Health checking
* Automatic failure recovery
* Circuit breakers
* Fault isolation
* Async programming
* Backend proxying
* Runtime load tracking
* Latency-aware decisions
* Persistent service configuration
* Redis integration
* PostgreSQL
* Containerization
* Automated testing
* Observability architecture

---

## 🔮 Roadmap

Planned improvements include:

* [ ] Distributed rate limiting
* [ ] Canary traffic routing
* [ ] Geo-aware routing
* [ ] Advanced Redis-based distributed coordination
* [ ] Prometheus metrics
* [ ] Grafana dashboards
* [ ] Locust load testing
* [ ] Chaos/failure testing
* [ ] SSRF protection
* [ ] React/Vite management dashboard
* [ ] Multi-instance deployment
* [ ] Kubernetes deployment

---

## 📊 Reliability Philosophy

Relay follows a simple principle:

> **Do not send traffic to a service that cannot reliably handle it.**

Instead of treating failures as exceptional events, Relay continuously observes backend health and adapts routing decisions accordingly.

```text
             ┌─────────────────────┐
             │      Incoming       │
             │       Traffic       │
             └──────────┬──────────┘
                        │
                        ▼
              ┌──────────────────┐
              │ Routing Decision  │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │ Backend Health   │
              │     Check        │
              └────────┬─────────┘
                       │
             ┌─────────┴─────────┐
             │                   │
          Healthy             Unhealthy
             │                   │
             ▼                   ▼
       Forward Traffic      Remove Traffic
             │                   │
             ▼                   ▼
       Track Metrics        Monitor Recovery
                                 │
                                 ▼
                         Restore Automatically
```

---

## 👩‍💻 Author

**Neeharika Reddy**

MCA — Computer Applications

Interested in:

* Backend Engineering
* Distributed Systems
* Reliability Engineering
* Software Development

GitHub: [Neeharika0305](https://github.com/Neeharika0305)

LinkedIn: [Neeharika Reddy](https://www.linkedin.com/in/neeharika-reddy-gadikota-646986276/)

---

## ⭐ Project

If you find the project interesting, consider giving it a ⭐.

**Relay — Intelligent traffic routing with reliability built in.**
