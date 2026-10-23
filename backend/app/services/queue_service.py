from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from fastapi import HTTPException
from app.db.models import ClinicQueue, PatientTicket
from app.schemas.clinic import ClinicUpdate
from app.core.config import settings

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

async def get_clinic_by_slug(db: AsyncSession, slug: str) -> ClinicQueue:
    """Retrieves clinic queue by slug or raises 404."""
    res = await db.execute(select(ClinicQueue).where(ClinicQueue.slug == slug))
    clinic = res.scalar_one_or_none()
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found.")
    return clinic

async def build_admin_overview(db: AsyncSession, clinic: ClinicQueue) -> dict:
    """Builds aggregated admin dashboard payload for doctor/receptionist."""
    # Waiting patients
    waiting_res = await db.execute(
        select(PatientTicket)
        .where(and_(PatientTicket.queue_id == clinic.id, PatientTicket.status == "waiting"))
        .order_by(PatientTicket.token_number.asc())
    )
    waiting_tickets = waiting_res.scalars().all()

    # Active / currently called
    active_res = await db.execute(
        select(PatientTicket)
        .where(and_(PatientTicket.queue_id == clinic.id, PatientTicket.status.in_(["called", "in_consultation"])))
        .order_by(PatientTicket.called_at.desc())
    )
    active_tickets = active_res.scalars().all()

    # Completed history
    history_res = await db.execute(
        select(PatientTicket)
        .where(and_(PatientTicket.queue_id == clinic.id, PatientTicket.status.in_(["completed", "no_show", "cancelled"])))
        .order_by(PatientTicket.completed_at.desc().nullslast(), PatientTicket.token_number.desc())
        .limit(25)
    )
    history_tickets = history_res.scalars().all()

    return {
        "clinic": {
            "id": clinic.id,
            "name": clinic.name,
            "slug": clinic.slug,
            "doctor_name": clinic.doctor_name,
            "avg_consultation_time_mins": clinic.avg_consultation_time_mins,
            "is_active": clinic.is_active,
            "qr_link": f"{settings.FRONTEND_BASE_URL.rstrip('/')}/q/{clinic.slug}",
            "qr_image_url": f"/api/queues/{clinic.slug}/qr"
        },
        "currently_serving": active_tickets[0] if active_tickets else None,
        "waiting_patients": waiting_tickets,
        "history_patients": history_tickets,
        "stats": {
            "total_waiting": len(waiting_tickets),
            "total_served_today": len([t for t in history_tickets if t.status == "completed"]),
            "estimated_next_wait_mins": len(waiting_tickets) * clinic.avg_consultation_time_mins
        }
    }

async def advance_queue(db: AsyncSession, clinic: ClinicQueue) -> dict:
    """Advances queue: completes current consultation and calls next waiting patient."""
    now = utc_now()
    curr_res = await db.execute(
        select(PatientTicket).where(
            and_(PatientTicket.queue_id == clinic.id, PatientTicket.status.in_(["called", "in_consultation"]))
        )
    )
    for ticket in curr_res.scalars().all():
        ticket.status = "completed"
        ticket.completed_at = now

    next_res = await db.execute(
        select(PatientTicket)
        .where(and_(PatientTicket.queue_id == clinic.id, PatientTicket.status == "waiting"))
        .order_by(PatientTicket.token_number.asc())
        .limit(1)
    )
    next_patient = next_res.scalar_one_or_none()
    if next_patient:
        next_patient.status = "called"
        next_patient.called_at = now

    await db.commit()
    return {
        "message": f"Called patient #{next_patient.token_number}" if next_patient else "Queue is empty.",
        "called_patient": next_patient
    }

async def change_ticket_status(db: AsyncSession, ticket_id: str, new_status: str) -> PatientTicket:
    """Updates status for a given ticket."""
    valid_statuses = {"waiting", "called", "in_consultation", "completed", "no_show", "cancelled"}
    if new_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {valid_statuses}")

    res = await db.execute(select(PatientTicket).where(PatientTicket.id == ticket_id))
    ticket = res.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found.")

    now = utc_now()
    ticket.status = new_status
    if new_status in ["completed", "no_show", "cancelled"]:
        ticket.completed_at = now
    elif new_status in ["called", "in_consultation"] and not ticket.called_at:
        ticket.called_at = now

    await db.commit()
    await db.refresh(ticket)
    return ticket
