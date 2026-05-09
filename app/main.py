"""FastAPI application exposing the dental CRM capabilities."""
from __future__ import annotations

from typing import Annotated, List

from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Session

from . import crud, database, schemas

app = FastAPI(title="Dental CRM", description="Clinic CRM for managing patients and finances")


@app.on_event("startup")
def on_startup() -> None:
    database.init_db()


SessionDep = Annotated[Session, Depends(database.get_session)]


@app.post("/doctors", response_model=schemas.DoctorRead, status_code=201)
def create_doctor(
    doctor_in: schemas.DoctorCreate, session: SessionDep
) -> schemas.DoctorRead:
    return schemas.DoctorRead.model_validate(crud.create_doctor(session, doctor_in))


@app.get("/doctors", response_model=List[schemas.DoctorRead])
def list_doctors(session: SessionDep) -> List[schemas.DoctorRead]:
    doctors = crud.list_doctors(session)
    return [schemas.DoctorRead.model_validate(doctor) for doctor in doctors]


@app.post("/patients", response_model=schemas.PatientRead, status_code=201)
def create_patient(
    patient_in: schemas.PatientCreate, session: SessionDep
) -> schemas.PatientRead:
    patient = crud.create_patient(session, patient_in)
    return schemas.PatientRead.model_validate(patient)


@app.get("/patients", response_model=List[schemas.PatientRead])
def list_patients(session: SessionDep) -> List[schemas.PatientRead]:
    patients = crud.list_patients(session)
    return [schemas.PatientRead.model_validate(patient) for patient in patients]


@app.get("/patients/{patient_id}", response_model=schemas.PatientRead)
def get_patient(patient_id: int, session: SessionDep) -> schemas.PatientRead:
    patient = crud.get_patient(session, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return schemas.PatientRead.model_validate(patient)


@app.post("/medical-notes", response_model=schemas.MedicalNoteRead, status_code=201)
def create_medical_note(
    note_in: schemas.MedicalNoteCreate, session: SessionDep
) -> schemas.MedicalNoteRead:
    note = crud.create_medical_note(session, note_in)
    return schemas.MedicalNoteRead.model_validate(note)


@app.get(
    "/patients/{patient_id}/medical-notes",
    response_model=List[schemas.MedicalNoteRead],
)
def list_patient_notes(patient_id: int, session: SessionDep) -> List[schemas.MedicalNoteRead]:
    notes = crud.list_patient_notes(session, patient_id)
    return [schemas.MedicalNoteRead.model_validate(note) for note in notes]


@app.post("/invoices", response_model=schemas.InvoiceRead, status_code=201)
def create_invoice(
    invoice_in: schemas.InvoiceCreate, session: SessionDep
) -> schemas.InvoiceRead:
    invoice = crud.create_invoice(session, invoice_in)
    return schemas.InvoiceRead.model_validate(invoice)


@app.get("/invoices", response_model=List[schemas.InvoiceRead])
def list_invoices(session: SessionDep) -> List[schemas.InvoiceRead]:
    invoices = crud.list_invoices(session)
    return [schemas.InvoiceRead.model_validate(invoice) for invoice in invoices]


@app.post("/payments", response_model=schemas.PaymentRead, status_code=201)
def create_payment(
    payment_in: schemas.PaymentCreate, session: SessionDep
) -> schemas.PaymentRead:
    payment = crud.create_payment(session, payment_in)
    return schemas.PaymentRead.model_validate(payment)


@app.get("/reports/financial", response_model=schemas.FinancialReport)
def financial_report(session: SessionDep) -> schemas.FinancialReport:
    return crud.get_financial_report(session)


@app.get("/reports/patients/{patient_id}", response_model=schemas.PatientReport)
def patient_report(patient_id: int, session: SessionDep) -> schemas.PatientReport:
    report = crud.get_patient_report(session, patient_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return report


@app.get(
    "/reports/doctors/productivity",
    response_model=List[schemas.DoctorProductivity],
)
def doctor_productivity(session: SessionDep) -> List[schemas.DoctorProductivity]:
    return list(crud.get_doctor_productivity(session))
