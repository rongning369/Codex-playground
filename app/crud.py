"""Database access helpers for the dental CRM system."""
from __future__ import annotations

from typing import Iterable, List, Optional

from sqlalchemy import func
from sqlmodel import Session, select

from . import models, schemas


def create_doctor(session: Session, doctor_in: schemas.DoctorCreate) -> models.Doctor:
    doctor = models.Doctor(**doctor_in.model_dump())
    session.add(doctor)
    session.commit()
    session.refresh(doctor)
    return doctor


def list_doctors(session: Session) -> List[models.Doctor]:
    return list(session.exec(select(models.Doctor)))


def get_doctor(session: Session, doctor_id: int) -> Optional[models.Doctor]:
    return session.get(models.Doctor, doctor_id)


def create_patient(session: Session, patient_in: schemas.PatientCreate) -> models.Patient:
    patient = models.Patient(**patient_in.model_dump())
    session.add(patient)
    session.commit()
    session.refresh(patient)
    return patient


def list_patients(session: Session) -> List[models.Patient]:
    return list(session.exec(select(models.Patient)))


def get_patient(session: Session, patient_id: int) -> Optional[models.Patient]:
    return session.get(models.Patient, patient_id)


def create_medical_note(
    session: Session, note_in: schemas.MedicalNoteCreate
) -> models.MedicalNote:
    note = models.MedicalNote(**note_in.model_dump())
    session.add(note)
    session.commit()
    session.refresh(note)
    return note


def list_patient_notes(session: Session, patient_id: int) -> List[models.MedicalNote]:
    statement = select(models.MedicalNote).where(models.MedicalNote.patient_id == patient_id)
    return list(session.exec(statement))


def create_invoice(session: Session, invoice_in: schemas.InvoiceCreate) -> models.Invoice:
    payload = invoice_in.model_dump(exclude_unset=True)
    invoice = models.Invoice(**payload)
    if invoice.status is None:
        invoice.status = "pending"
    session.add(invoice)
    session.commit()
    session.refresh(invoice)
    return invoice


def list_invoices(session: Session) -> List[models.Invoice]:
    return list(session.exec(select(models.Invoice)))


def _update_invoice_status_from_payments(session: Session, invoice: models.Invoice) -> None:
    paid_total = session.exec(
        select(func.coalesce(func.sum(models.Payment.amount), 0)).where(
            models.Payment.invoice_id == invoice.id
        )
    ).one()
    if paid_total >= invoice.amount:
        invoice.status = "paid"
    elif paid_total > 0:
        invoice.status = "partial"
    else:
        invoice.status = "pending"


def create_payment(session: Session, payment_in: schemas.PaymentCreate) -> models.Payment:
    payment = models.Payment(**payment_in.model_dump(exclude_unset=True))
    session.add(payment)
    session.commit()
    session.refresh(payment)

    invoice = session.get(models.Invoice, payment.invoice_id)
    if invoice is not None:
        _update_invoice_status_from_payments(session, invoice)
        session.add(invoice)
        session.commit()
        session.refresh(invoice)

    return payment


def list_payments(session: Session) -> List[models.Payment]:
    return list(session.exec(select(models.Payment)))


def get_financial_report(session: Session) -> schemas.FinancialReport:
    total_invoiced = session.exec(
        select(func.coalesce(func.sum(models.Invoice.amount), 0))
    ).one()
    total_paid = session.exec(
        select(func.coalesce(func.sum(models.Payment.amount), 0))
    ).one()
    pending_invoices = session.exec(
        select(func.count()).where(models.Invoice.status != "paid")
    ).one()
    paid_invoices = session.exec(
        select(func.count()).where(models.Invoice.status == "paid")
    ).one()

    outstanding = float(total_invoiced - total_paid)

    return schemas.FinancialReport(
        total_invoiced=float(total_invoiced),
        total_paid=float(total_paid),
        outstanding_balance=outstanding,
        pending_invoices=pending_invoices,
        paid_invoices=paid_invoices,
    )


def get_patient_report(session: Session, patient_id: int) -> Optional[schemas.PatientReport]:
    patient = session.get(models.Patient, patient_id)
    if patient is None:
        return None

    total_invoiced = session.exec(
        select(func.coalesce(func.sum(models.Invoice.amount), 0)).where(
            models.Invoice.patient_id == patient_id
        )
    ).one()
    total_paid = session.exec(
        select(func.coalesce(func.sum(models.Payment.amount), 0)).join(
            models.Invoice,
            models.Invoice.id == models.Payment.invoice_id,
            isouter=True,
        ).where(models.Invoice.patient_id == patient_id)
    ).one()
    notes_count = session.exec(
        select(func.count()).where(models.MedicalNote.patient_id == patient_id)
    ).one()

    return schemas.PatientReport(
        patient=schemas.PatientRead(**patient.model_dump()),
        total_invoiced=float(total_invoiced),
        total_paid=float(total_paid),
        outstanding_balance=float(total_invoiced - total_paid),
        notes_count=notes_count,
    )


def get_doctor_productivity(session: Session) -> Iterable[schemas.DoctorProductivity]:
    doctors = list(session.exec(select(models.Doctor)))
    for doctor in doctors:
        patient_count = session.exec(
            select(func.count()).where(models.Patient.primary_doctor_id == doctor.id)
        ).one()
        notes_authored = session.exec(
            select(func.count()).where(models.MedicalNote.doctor_id == doctor.id)
        ).one()
        yield schemas.DoctorProductivity(
            doctor_id=doctor.id,
            doctor_name=doctor.full_name,
            patient_count=patient_count,
            notes_authored=notes_authored,
        )
