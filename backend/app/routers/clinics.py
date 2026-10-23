from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.db.database import get_db
from app.db.models import ClinicQueue, PatientTicket
from app.schemas.clinic import ClinicCreate, ClinicResponse, ClinicPublicInfo, ClinicUpdate
from app.core.cache import cache

router = APIRouter(prefix="/api", tags=["Clinics"])

@router.post("/queues", response_model=ClinicResponse, status_code=status.HTTP_201_CREATED)
async def create_clinic(payload: ClinicCreate, db: AsyncSession = Depends(get_db)):
    """Create a new clinic queue."""
    existing = await db.execute(select(ClinicQueue).where(ClinicQueue.slug == payload.slug.strip().lower()))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Clinic slug already exists.")

    clinic = ClinicQueue(
        name=payload.name.strip(),
        slug=payload.slug.strip().lower(),
        doctor_name=payload.doctor_name.strip(),
        avg_consultation_time_mins=payload.avg_consultation_time_mins,
        is_active=payload.is_active
    )
    db.add(clinic)
    await db.commit()
    await db.refresh(clinic)
    return clinic

@router.get("/queues", response_model=list[ClinicResponse])
async def list_clinics(db: AsyncSession = Depends(get_db)):
    """List all clinics."""
    res = await db.execute(select(ClinicQueue).order_by(ClinicQueue.created_at.desc()))
    return res.scalars().all()

@router.get("/queues/{slug}/info", response_model=ClinicPublicInfo)
async def get_clinic_public_info(slug: str, db: AsyncSession = Depends(get_db)):
    """Public info for intake check-in screen."""
    res = await db.execute(select(ClinicQueue).where(ClinicQueue.slug == slug))
    clinic = res.scalar_one_or_none()
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found.")

    waiting_res = await db.execute(
        select(func.count(PatientTicket.id))
        .where(and_(PatientTicket.queue_id == clinic.id, PatientTicket.status.in_(["waiting", "called", "in_consultation"])))
    )
    total_waiting = waiting_res.scalar_one()

    curr_res = await db.execute(
        select(PatientTicket)
        .where(and_(PatientTicket.queue_id == clinic.id, PatientTicket.status.in_(["called", "in_consultation"])))
        .order_by(PatientTicket.called_at.desc())
        .limit(1)
    )
    curr = curr_res.scalar_one_or_none()

    return ClinicPublicInfo(
        id=clinic.id,
        name=clinic.name,
        slug=clinic.slug,
        doctor_name=clinic.doctor_name,
        avg_consultation_time_mins=clinic.avg_consultation_time_mins,
        is_active=clinic.is_active,
        total_waiting=total_waiting,
        currently_serving_token=curr.token_number if curr else None,
        currently_serving_patient=curr.patient_name if curr else None,
        qr_url=f"/api/queues/{clinic.slug}/qr"
    )

@router.patch("/queues/{slug}", response_model=ClinicResponse)
async def update_clinic(slug: str, payload: ClinicUpdate, db: AsyncSession = Depends(get_db)):
    """Update clinic queue settings."""
    res = await db.execute(select(ClinicQueue).where(ClinicQueue.slug == slug))
    clinic = res.scalar_one_or_none()
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found.")

    if payload.name is not None:
        clinic.name = payload.name.strip()
    if payload.doctor_name is not None:
        clinic.doctor_name = payload.doctor_name.strip()
    if payload.avg_consultation_time_mins is not None:
        clinic.avg_consultation_time_mins = payload.avg_consultation_time_mins
    if payload.is_active is not None:
        clinic.is_active = payload.is_active

    await db.commit()
    await db.refresh(clinic)
    await cache.invalidate_queue(clinic.id)
    return clinic
