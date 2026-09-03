from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import date, datetime, time
from typing import Optional
from app.models.clinic import AppointmentStatus, RoleEnum

class UserBase(BaseModel):
    email: EmailStr
    role: RoleEnum

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class DoctorCreate(BaseModel):
    user: UserCreate
    name: str
    crm: Optional[str] = None

class DoctorResponse(BaseModel):
    id: int
    name: str
    crm: Optional[str]
    user: UserResponse
    model_config = ConfigDict(from_attributes=True)

class PatientCreate(BaseModel):
    user: UserCreate
    name: str
    phone: str

class PatientResponse(BaseModel):
    id: int
    name: str
    phone: str
    user: UserResponse
    model_config = ConfigDict(from_attributes=True)

class AppointmentCreate(BaseModel):  
    doctor_id: int
    patient_id: int
    date_consultation: date
    consultation_time: time

class AppointmentResponse(AppointmentCreate):

    id: int
    status: AppointmentStatus
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)