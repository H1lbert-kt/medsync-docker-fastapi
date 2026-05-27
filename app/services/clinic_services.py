from sqlalchemy.orm import Session
from datetime import date, time
from fastapi import status, HTTPException

from app.models.clinic import DoctorModel, AppointmentModel, AppointmentStatus, PatientModel
from app.schemas.clinic import DoctorCreate, PatientCreate, AppointmentCreate

def doctor_create(db: Session, doctor_data: DoctorCreate):
    new_doctor = DoctorModel(name=doctor_data.name)
    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)
    return new_doctor

def patient_create(db: Session, patient_data: PatientCreate):
    new_patient = PatientModel(name=patient_data.name, phone=patient_data.phone)
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient

def create_appointment(db: Session, appointment_data: AppointmentCreate):
    
    conflict = db.query(AppointmentModel).filter(AppointmentModel.doctor_id == appointment_data.doctor_id,
                                                 AppointmentModel.date_consultation == appointment_data.date_consultation,
                                                 AppointmentModel.consultation_time == appointment_data.consultation_time,
                                                 AppointmentModel.status != AppointmentStatus.CANCELLED.value).first()
    
    if conflict:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Este médico já possui um atendimento para este dia e horário.")
    

    new_appointment = AppointmentModel(doctor_id=appointment_data.doctor_id,
                                                        patient_id=appointment_data.patient_id,
                                                        date_consultation=appointment_data.date_consultation,
                                                        consultation_time=appointment_data.consultation_time)
    
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    return new_appointment