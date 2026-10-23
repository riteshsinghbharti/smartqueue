from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class PatientJoinRequest(BaseModel):
    patient_name: str = Field(..., min_length=2, max_length=255, json_schema_extra={"example": "John Doe"})
    age: int = Field(..., ge=0, le=130, json_schema_extra={"example": 32})
    gender: str = Field(..., json_schema_extra={"example": "Male"})
    note: Optional[str] = Field(None, max_length=500, json_schema_extra={"example": "Fever and sore throat"})

class PatientTicketResponse(BaseModel):
    id: str
    queue_id: str
    token_number: int
    patient_name: str
    age: int
    gender: str
    note: Optional[str] = None
    status: str
    joined_at: datetime
    called_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class PatientTicketLiveStatus(BaseModel):
    ticket_id: str
    token_number: int
    patient_name: str
    clinic_name: str
    doctor_name: str
    status: str
    position_ahead: int
    estimated_wait_mins: int
    total_waiting_in_clinic: int
    currently_serving_token: Optional[int] = None
    currently_serving_patient: Optional[str] = None
    avg_consultation_time_mins: int
    joined_at: datetime
    called_at: Optional[datetime] = None
    is_up_next: bool = False

class UpdateTicketStatusRequest(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "in_consultation"})
