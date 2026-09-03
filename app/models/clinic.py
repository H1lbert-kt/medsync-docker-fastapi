from datetime import datetime, timezone
import enum
from sqlalchemy import Integer, String, ForeignKey, Column, DateTime, Date, Time, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class RoleEnum(str, enum.Enum):
    ADMIN = "ADMIN"
    RECEPTIONIST = "RECEPTIONIST"
    DOCTOR = "DOCTOR"
    PATIENT = "PATIENT"

class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)

    doctor = relationship("DoctorModel", back_populates="user", uselist=False)
    patient = relationship("PatientModel", back_populates="user", uselist=False)

class DoctorModel(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    crm = Column(String(20), unique=True, nullable=True)

    user = relationship("UserModel", back_populates="doctor")
    appointments = relationship("AppointmentModel", back_populates="doctor")

class PatientModel(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)

    user = relationship("UserModel", back_populates="patient")
    appointments = relationship("AppointmentModel", back_populates="patient")

class AppointmentModel(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id", ondelete="RESTRICT"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="RESTRICT"), nullable=False)
    date_consultation = Column(Date, nullable=False)
    consultation_time = Column(Time, nullable=False)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    doctor = relationship("DoctorModel", back_populates="appointments")
    patient = relationship("PatientModel", back_populates="appointments")

    __table_args__ = (
        UniqueConstraint("doctor_id", "date_consultation", "consultation_time", name="uq_doctor_appointment_schedule"),
    )