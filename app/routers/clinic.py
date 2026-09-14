from fastapi import APIRouter, Depends, Path, status, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.clinic import (
    RoleEnum, UserModel, DoctorModel, PatientModel, AppointmentModel, AppointmentStatus
)
from app.schemas.clinic import (
    DoctorCreate, DoctorResponse,
    PatientCreate, PatientResponse,
    AppointmentCreate, AppointmentResponse
)
from app.services import clinic_services
from app.core.dependencies import require_roles, get_current_user

router = APIRouter(prefix="/clinic", tags=["Clinic"])

@router.post("/doctors", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
def doctor_register(
    doctor_data: DoctorCreate, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_roles([RoleEnum.ADMIN]))
):
    return clinic_services.doctor_create(db=db, doctor_data=doctor_data)

@router.post("/patients", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def patient_register(
    patient_data: PatientCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_roles([RoleEnum.ADMIN, RoleEnum.RECEPTIONIST]))
):
    return clinic_services.patient_create(db=db, patient_data=patient_data)

@router.post("/appointments", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def appointment_register(
    appointment_data: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_roles([RoleEnum.ADMIN, RoleEnum.RECEPTIONIST, RoleEnum.PATIENT]))
):
    if current_user.role == RoleEnum.PATIENT:
        patient = db.query(PatientModel).filter(PatientModel.user_id == current_user.id).first()
        if not patient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found.")
        appointment_data.patient_id = patient.id

    return clinic_services.create_appointment(db=db, appointment_data=appointment_data)

@router.get("/doctors", response_model=list[DoctorResponse])
def list_doctors(db: Session = Depends(get_db),
                 current_user: UserModel = Depends(require_roles([RoleEnum.ADMIN, RoleEnum.RECEPTIONIST]))
):
    return db.query(DoctorModel).all()

@router.get("/patients", response_model=list[PatientResponse])
def list_patients(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_roles([RoleEnum.ADMIN, RoleEnum.RECEPTIONIST]))
):
    return db.query(PatientModel).all()

@router.get("/appointments", response_model=list[AppointmentResponse])
def list_appointments(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if current_user.role == RoleEnum.PATIENT:
        patient = db.query(PatientModel).filter(PatientModel.user_id == current_user.id).first()
        if not patient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found.")
        return db.query(AppointmentModel).filter(AppointmentModel.patient_id == patient.id).all()
    if current_user.role == RoleEnum.DOCTOR:
        doctor = db.query(DoctorModel).filter(DoctorModel.user_id == current_user.id).first()
        if not doctor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found.")
        return db.query(AppointmentModel).filter(AppointmentModel.doctor_id == doctor.id).all()
    return db.query(AppointmentModel).all()

@router.patch("/appointments/{appointment_id}/cancel", response_model=AppointmentResponse)
def cancel_appointment(
    appointment_id: int = Path(...),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):

    appointment = db.query(AppointmentModel).filter(AppointmentModel.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found.")

    if current_user.role == RoleEnum.PATIENT:
        patient = db.query(PatientModel).filter(PatientModel.user_id == current_user.id).first()
        if not patient or appointment.patient_id != patient.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only cancel your own appointments.")

    appointment.status = AppointmentStatus.CANCELLED
    db.commit()
    db.refresh(appointment)
    return appointment

