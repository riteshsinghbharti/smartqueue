# smartqueue

`import "graveyard/backend"`

Package `smartqueue` provides a real-time virtual queue and token management service designed for healthcare clinics and outpatient departments (OPDs).

---

## Overview

Package `smartqueue` eliminates physical waiting room congestion. Patients register by scanning a counter QR code, receive a sequential digital token, and track an animated visual queue alongside an estimated wait time on their mobile devices. Doctors and clinic staff advance the queue from a dedicated console.

### Key Characteristics

- **Zero-Latency Smart Polling**: High-frequency patient polling requests (every 5 seconds) are served from an in-memory cache in sub-millisecond time (`< 2ms`), protecting disk storage from read contention.
- **Embedded SQLite Engine**: Operates with self-contained asynchronous SQLite (`aiosqlite`), requiring zero external database configuration or cloud database costs.
- **Container Ready**: Packaged via a multi-stage Docker build producing a secure, non-root minimal runtime image.
- **Active Keep-Alive**: Exposes `/health` for scheduled 10-minute ping services (e.g. cron-job.org) preventing sleeping instances on free-tier container platforms.

---

## Architecture

The system follows SOLID principles with strict separation of concerns:

```
backend/
├── app/
│   ├── core/
│   │   ├── config.py          // Application settings via pydantic-settings
│   │   └── cache.py           // InMemoryCache with TTL and queue-level invalidation
│   ├── db/
│   │   ├── database.py        // Async SQLAlchemy engine and session factory
│   │   └── models.py          // ClinicQueue and PatientTicket ORM declarations
│   ├── routers/
│   │   ├── health.py          // GET /health keep-alive endpoint
│   │   ├── clinics.py         // Clinic registration and public metadata
│   │   ├── admin.py           // Doctor console and queue advancement
│   │   └── patients.py        // Patient intake and smart-polling ticket status
│   ├── schemas/
│   │   ├── clinic.py          // Pydantic request/response models for clinics
│   │   └── patient.py         // Pydantic request/response models for patients
│   ├── services/
│   │   ├── queue_service.py   // Queue orchestration and status transition logic
│   │   ├── patient_service.py // Intake processing and position calculation
│   │   └── qr_service.py      // PNG QR code generation
│   └── main.py                // Application entry point, lifespan, CORS
└── tests/                     // Pytest integration and unit test suite
```

---

## Configuration

Settings are loaded via environment variables or a `.env` file at the root of `backend/`:

| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `DATABASE_URL` | string | `sqlite+aiosqlite:///./clinic_queue.db` | Path to SQLite database file |
| `CORS_ORIGINS` | string | `http://localhost:5173,...` | Comma-delimited list of permitted CORS origins |
| `FRONTEND_BASE_URL` | string | `http://localhost:5173` | Target domain encoded into patient QR codes |
| `PORT` | int | `8000` | Port listened to by the ASGI server |
| `CACHE_TTL_SECONDS` | int | `30` | Fallback TTL for cached patient status entries |

---

## Quick Start

### 1. Installation

```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1

# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Run Server

```bash
uvicorn app.main:app --reload --port 8000
```

- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Default Clinic Seed: http://localhost:8000/api/queues/apex-clinic/info

---

## Deployment (Render & Vercel)

### 1. Backend on Render

1. Create a **Web Service** on Render connected to your repository.
2. Select **Docker** environment (Render automatically uses `backend/Dockerfile`).
3. Root Directory: `backend`.
4. *Render Disk / Volume (Optional)*:
   - On Render Free Tier, the database file `/app/clinic_queue.db` lives inside the container. Combined with your 10-minute cron keep-alive ping on `/health`, the container stays warm 24/7 throughout your hackathon demo.
   - If using a paid Render Persistent Disk mounted at `/data`, set:
     `DATABASE_URL=sqlite+aiosqlite:////data/clinic_queue.db`.

### 2. Keep-Alive Cron Ping (Every 10 Mins)

1. Set up a free monitor at [cron-job.org](https://cron-job.org) or [UptimeRobot](https://uptimerobot.com).
2. URL: `https://<your-render-app>.onrender.com/health`
3. Interval: Every 10 minutes.

---

## Testing

Tests are located in `backend/tests/` and run using `pytest`:

```bash
cd backend
pytest tests -v
```
