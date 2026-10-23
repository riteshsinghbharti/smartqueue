from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter(tags=["Health"])

@router.get("/health")
@router.get("/api/health")
async def health_check():
    """
    Health check endpoint for Render free tier keep-alive ping.
    Expected to be hit every 10 minutes by a cron-job / uptime monitor.
    """
    return {
        "status": "healthy",
        "service": "clinic-virtual-queue-backend",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
