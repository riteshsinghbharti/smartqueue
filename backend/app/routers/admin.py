from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas.patient import UpdateTicketStatusRequest
from app.services.queue_service import (
    get_clinic_by_slug,
    build_admin_overview,
    advance_queue,
    change_ticket_status,
)
from app.services.qr_service import build_clinic_qr_png
from app.core.cache import cache

router = APIRouter(prefix="/api", tags=["Doctor & Admin Console"])

@router.get("/queues/{slug}/admin")
async def get_admin_dashboard(slug: str, db: AsyncSession = Depends(get_db)):
    """Admin dashboard overview for receptionist or doctor."""
    clinic = await get_clinic_by_slug(db, slug)
    return await build_admin_overview(db, clinic)

@router.post("/queues/{slug}/call-next")
async def call_next(slug: str, db: AsyncSession = Depends(get_db)):
    """Advances queue to the next waiting patient and invalidates cache."""
    clinic = await get_clinic_by_slug(db, slug)
    result = await advance_queue(db, clinic)
    await cache.invalidate_queue(clinic.id)
    return result

@router.post("/tickets/{ticket_id}/status")
async def update_status(
    ticket_id: str,
    payload: UpdateTicketStatusRequest,
    db: AsyncSession = Depends(get_db)
):
    """Change status for a single ticket."""
    ticket = await change_ticket_status(db, ticket_id, payload.status)
    await cache.invalidate_queue(ticket.queue_id)
    return ticket

@router.get("/queues/{slug}/qr")
async def get_clinic_qr(slug: str, db: AsyncSession = Depends(get_db)):
    """Generates PNG QR code for clinic entrance/reception."""
    await get_clinic_by_slug(db, slug)
    qr_bytes = build_clinic_qr_png(slug)
    return Response(content=qr_bytes, media_type="image/png")
