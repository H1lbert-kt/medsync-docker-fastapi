from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from datetime import date, datetime, time
from typing import Optional
from app.models.clinic import AppointmentStatus, RoleEnum

class Token(BaseModel):
    access_token: str
    token_type: str

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

    @field_validator("date_consultation")
    @classmethod
    def date_not_in_past(cls, v):
        if v < date.today():
            raise ValueError("Cannot schedule appointments in the past.")
        return v

    @field_validator("consultation_time")
    @classmethod
    def time_not_in_past(cls, v, info):
        from datetime import datetime, timezone
        date_val = info.data.get("date_consultation")
        if date_val and date_val == date.today():
            now = datetime.now(timezone.utc).time()
            if v < now:
                raise ValueError("Cannot schedule appointments for a time that has already passed.")
        return v

class AppointmentResponse(AppointmentCreate):

    id: int
    status: AppointmentStatus
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)