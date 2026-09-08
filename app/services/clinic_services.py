from typing import Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi import status, HTTPException

from app.models.clinic import UserModel, DoctorModel, AppointmentModel, AppointmentStatus, PatientModel
from app.schemas.clinic import DoctorCreate, PatientCreate, AppointmentCreate
from app.core.security import verify_password, get_password_hash

def authenticate_user(db: Session, email: str, password: str) -> Optional[UserModel]:
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

def doctor_create(db: Session, doctor_data: DoctorCreate) -> DoctorModel:
    hashed_password = get_password_hash(doctor_data.user.password)

    new_user = UserModel(
        email=doctor_data.user.email,
        password_hash=hashed_password,
        role=doctor_data.user.role
    )
    db.add(new_user)

    try:
        db.flush()
        new_doctor = DoctorModel(
            user_id=new_user.id,
            name=doctor_data.name,
            crm=doctor_data.crm
        )
        db.add(new_doctor)
        db.commit()
        db.refresh(new_doctor)
        return new_doctor
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or crm already registered in the system."
        )

def patient_create(db: Session, patient_data: PatientCreate) -> PatientModel:
    hashed_password = get_password_hash(patient_data.user.password)

    new_user = UserModel(
        email=patient_data.user.email,
        password_hash=hashed_password,
        role=patient_data.user.role
    )
    db.add(new_user)

    try:
        db.flush()
        new_patient = PatientModel(
            user_id=new_user.id,
            name=patient_data.name,
            phone=patient_data.phone
        )
        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)
        return new_patient
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered in the system."
        )

def create_appointment(db: Session, appointment_data: AppointmentCreate):
    doctor_exists = db.query(DoctorModel.id).filter(DoctorModel.id == appointment_data.doctor_id).first()
    if not doctor_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found."
        )

    patient_exists = db.query(PatientModel.id).filter(PatientModel.id == appointment_data.patient_id).first()
    if not patient_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found."
        )

    new_appointment = AppointmentModel(
        doctor_id=appointment_data.doctor_id,
        patient_id=appointment_data.patient_id,
        date_consultation=appointment_data.date_consultation,
        consultation_time=appointment_data.consultation_time,
        status=AppointmentStatus.SCHEDULED
    )
    db.add(new_appointment)

    try:
        db.commit()
        db.refresh(new_appointment)
        return new_appointment
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The doctor already has an appointment scheduled for this date and time."
        )