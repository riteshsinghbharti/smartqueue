from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas.patient import PatientJoinRequest, PatientTicketResponse, PatientTicketLiveStatus
from app.services.patient_service import add_patient_to_queue, compute_patient_status
from app.core.cache import cache
from app.core.config import settings

router = APIRouter(prefix="/api", tags=["Patients"])

@router.post("/queues/{slug}/join", response_model=PatientTicketResponse, status_code=status.HTTP_201_CREATED)
async def join_queue(
    slug: str,
    payload: PatientJoinRequest,
    db: AsyncSession = Depends(get_db)
):
    """Register patient in queue and invalidate cache."""
    ticket = await add_patient_to_queue(db, slug, payload)
    await cache.invalidate_queue(ticket.queue_id)
    return ticket

@router.get("/tickets/{ticket_id}/status", response_model=PatientTicketLiveStatus)
async def get_ticket_status(
    ticket_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Smart-polling endpoint served directly from memory cache when available.
    """
    cache_key = f"ticket_status:{ticket_id}"
    cached = await cache.get(cache_key)
    if cached:
        return cached

    # Compute status and cache
    live_status = await compute_patient_status(db, ticket_id)
    await cache.set(
        cache_key,
        live_status.model_dump(),
        ttl=settings.CACHE_TTL_SECONDS
    )
    return live_status
