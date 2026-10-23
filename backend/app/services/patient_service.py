from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from fastapi import HTTPException
from app.db.models import ClinicQueue, PatientTicket
from app.schemas.patient import PatientJoinRequest, PatientTicketLiveStatus

async def add_patient_to_queue(
    db: AsyncSession,
    slug: str,
    payload: PatientJoinRequest
) -> PatientTicket:
    """Inserts patient into queue with the next sequential token number."""
    res = await db.execute(select(ClinicQueue).where(ClinicQueue.slug == slug))
    clinic = res.scalar_one_or_none()
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found.")
    
    if not clinic.is_active:
        raise HTTPException(status_code=400, detail="Clinic queue is currently paused.")

    # Determine next token number
    token_res = await db.execute(
        select(func.coalesce(func.max(PatientTicket.token_number), 0))
        .where(PatientTicket.queue_id == clinic.id)
    )
    next_token = token_res.scalar_one() + 1

    ticket = PatientTicket(
        queue_id=clinic.id,
        token_number=next_token,
        patient_name=payload.patient_name.strip(),
        age=payload.age,
        gender=payload.gender,
        note=payload.note.strip() if payload.note else None,
        status="waiting"
    )
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    return ticket


async def compute_patient_status(
    db: AsyncSession,
    ticket_id: str
) -> PatientTicketLiveStatus:
    """Computes real-time position ahead and estimated wait for smart polling."""
    res = await db.execute(
        select(PatientTicket, ClinicQueue)
        .join(ClinicQueue, PatientTicket.queue_id == ClinicQueue.id)
        .where(PatientTicket.id == ticket_id)
    )
    row = res.first()
    if not row:
        raise HTTPException(status_code=404, detail="Ticket not found.")
    
    ticket, clinic = row

    position_ahead = 0
    if ticket.status == "waiting":
        pos_res = await db.execute(
            select(func.count(PatientTicket.id)).where(
                and_(
                    PatientTicket.queue_id == clinic.id,
                    PatientTicket.status == "waiting",
                    PatientTicket.token_number < ticket.token_number
                )
            )
        )
        waiting_ahead = pos_res.scalar_one()

        serving_res = await db.execute(
            select(func.count(PatientTicket.id)).where(
                and_(
                    PatientTicket.queue_id == clinic.id,
                    PatientTicket.status.in_(["called", "in_consultation"])
                )
            )
        )
        position_ahead = waiting_ahead + serving_res.scalar_one()

    # Total active patients
    total_res = await db.execute(
        select(func.count(PatientTicket.id)).where(
            and_(
                PatientTicket.queue_id == clinic.id,
                PatientTicket.status.in_(["waiting", "called", "in_consultation"])
            )
        )
    )
    total_waiting = total_res.scalar_one()

    # Current serving patient
    curr_res = await db.execute(
        select(PatientTicket).where(
            and_(
                PatientTicket.queue_id == clinic.id,
                PatientTicket.status.in_(["called", "in_consultation"])
            )
        )
        .order_by(PatientTicket.called_at.desc())
        .limit(1)
    )
    curr_ticket = curr_res.scalar_one_or_none()

    estimated_wait = position_ahead * clinic.avg_consultation_time_mins
    is_up_next = (ticket.status == "waiting" and position_ahead <= 1) or ticket.status == "called"

    return PatientTicketLiveStatus(
        ticket_id=ticket.id,
        token_number=ticket.token_number,
        patient_name=ticket.patient_name,
        clinic_name=clinic.name,
        doctor_name=clinic.doctor_name,
        status=ticket.status,
        position_ahead=position_ahead,
        estimated_wait_mins=estimated_wait,
        total_waiting_in_clinic=total_waiting,
        currently_serving_token=curr_ticket.token_number if curr_ticket else None,
        currently_serving_patient=curr_ticket.patient_name if curr_ticket else None,
        avg_consultation_time_mins=clinic.avg_consultation_time_mins,
        joined_at=ticket.joined_at,
        called_at=ticket.called_at,
        is_up_next=is_up_next
    )
