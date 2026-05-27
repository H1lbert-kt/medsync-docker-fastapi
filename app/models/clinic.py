from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Integer, String, ForeignKey, Column, DateTime, Date, Time
from sqlalchemy.orm import relationship
from app.database import Base

class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"

class DoctorModel(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)

class PatientModel(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)

class AppointmentModel(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    date_consultation = Column(Date, nullable=False)
    consultation_time = Column(Time, nullable=False)
    status = Column(String(30), default=AppointmentStatus.SCHEDULED.value, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
