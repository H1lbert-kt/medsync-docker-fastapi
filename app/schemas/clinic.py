from pydantic import BaseModel, Field
from datetime import date, datetime, time
from app.models.clinic import AppointmentStatus

class DoctorBase(BaseModel):

    name: str = Field(max_length=100, min_length=8, examples=["Dr. Hilbert"])

class DoctorCreate(DoctorBase):
    pass

class DoctorResponse(DoctorBase):

    id: int
    
    model_config = {"from_attributes": True}

class PatientBase(BaseModel):
    
    name: str = Field(max_length=100, min_length=8)
    phone: str = Field(max_length=20, min_length=11)

class PatientCreate(PatientBase):
    
    pass


class PatientResponse(PatientBase):
    
    id: int

    model_config = {"from_attributes":True}

class AppointmentBase(BaseModel):

    date_consultation: date
    consultation_time: time

class AppointmentCreate(AppointmentBase):
    
    doctor_id: int
    patient_id: int

class AppointmentResponse(AppointmentBase):

    id: int
    status: AppointmentStatus
    created_at: datetime

    model_config = {"from_attributes": True}