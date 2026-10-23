import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.core.config import settings
from app.core.cache import cache
from app.db.database import engine, Base, AsyncSessionLocal
from app.db.models import ClinicQueue
from app.routers import health, clinics, admin, patients

async def seed_demo_clinic():
    """Seeds a demo clinic if no clinics exist, allowing instant testing."""
    async with AsyncSessionLocal() as session:
        try:
            res = await session.execute(select(ClinicQueue).limit(1))
            if not res.scalar_one_or_none():
                demo = ClinicQueue(
                    name="Apex Healthcare & Wellness Clinic",
                    slug="apex-clinic",
                    doctor_name="Dr. Sarah Mehta, MD",
                    avg_consultation_time_mins=10,
                    is_active=True
                )
                session.add(demo)
                await session.commit()
        except Exception:
            pass

async def periodic_cache_cleanup():
    """Background task to remove expired keys every 60 seconds."""
    while True:
        try:
            await asyncio.sleep(60)
            await cache.clear_expired()
        except asyncio.CancelledError:
            break
        except Exception:
            pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_demo_clinic()
    task = asyncio.create_task(periodic_cache_cleanup())
    yield
    task.cancel()
    await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="High-performance backend for clinic virtual queues with in-memory caching.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
origins = settings.cors_origins_list
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if "*" not in origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router Registration
app.include_router(health.router)
app.include_router(clinics.router)
app.include_router(admin.router)
app.include_router(patients.router)

@app.get("/")
async def root():
    return {
        "project": settings.PROJECT_NAME,
        "status": "online",
        "docs": "/docs",
        "health": "/health",
        "demo_clinic": "/api/queues/apex-clinic/info"
    }

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
