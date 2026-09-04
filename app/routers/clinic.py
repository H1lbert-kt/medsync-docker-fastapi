from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.clinic import RoleEnum, UserModel
from app.schemas.clinic import (
    DoctorCreate, DoctorResponse,
    PatientCreate, PatientResponse,
    AppointmentCreate, AppointmentResponse
)
from app.services import clinic_services
from app.core.dependencies import require_roles

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
    return clinic_services.create_appointment(db=db, appointment_data=appointment_data)

