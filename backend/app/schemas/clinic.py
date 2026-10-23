from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class ClinicBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, json_schema_extra={"example": "Apex Healthcare Clinic"})
    slug: str = Field(..., min_length=2, max_length=100, json_schema_extra={"example": "apex-clinic"})
    doctor_name: str = Field(..., min_length=2, max_length=255, json_schema_extra={"example": "Dr. Sarah Mehta"})
    avg_consultation_time_mins: int = Field(default=10, ge=1, le=120)
    is_active: bool = True

class ClinicCreate(ClinicBase):
    pass

class ClinicUpdate(BaseModel):
    name: Optional[str] = None
    doctor_name: Optional[str] = None
    avg_consultation_time_mins: Optional[int] = Field(None, ge=1, le=120)
    is_active: Optional[bool] = None

class ClinicResponse(ClinicBase):
    id: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ClinicPublicInfo(BaseModel):
    id: str
    name: str
    slug: str
    doctor_name: str
    avg_consultation_time_mins: int
    is_active: bool
    total_waiting: int
    currently_serving_token: Optional[int] = None
    currently_serving_patient: Optional[str] = None
    qr_url: str
