import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.database import Base

def generate_uuid():
    return str(uuid.uuid4())

def utc_now():
    return datetime.now(timezone.utc)

class ClinicQueue(Base):
    __tablename__ = "clinics"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    doctor_name = Column(String(255), nullable=False)
    avg_consultation_time_mins = Column(Integer, default=10, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    tickets = relationship("PatientTicket", back_populates="clinic", cascade="all, delete-orphan", order_by="PatientTicket.token_number")

class PatientTicket(Base):
    __tablename__ = "patient_tickets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    queue_id = Column(String(36), ForeignKey("clinics.id", ondelete="CASCADE"), nullable=False, index=True)
    token_number = Column(Integer, nullable=False)
    patient_name = Column(String(255), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(50), nullable=False)
    note = Column(Text, nullable=True)
    status = Column(String(50), default="waiting", nullable=False, index=True) 
    # Statuses: 'waiting', 'called', 'in_consultation', 'completed', 'no_show', 'cancelled'
    joined_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    called_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    clinic = relationship("ClinicQueue", back_populates="tickets")
