"""Pydantic/SQLModel schemas exposed via the API."""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlmodel import SQLModel


class DoctorBase(SQLModel):
    full_name: str
    specialty: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class DoctorCreate(DoctorBase):
    pass


class DoctorRead(DoctorBase):
    id: int


class PatientBase(SQLModel):
    full_name: str
    date_of_birth: date
    contact_phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    primary_doctor_id: Optional[int] = None


class PatientCreate(PatientBase):
    pass


class PatientRead(PatientBase):
    id: int


class MedicalNoteCreate(SQLModel):
    patient_id: int
    doctor_id: int
    note: str


class MedicalNoteRead(MedicalNoteCreate):
    id: int
    created_at: datetime


class InvoiceCreate(SQLModel):
    patient_id: int
    amount: float
    description: Optional[str] = None
    status: Optional[str] = None
    issued_date: Optional[date] = None


class InvoiceRead(InvoiceCreate):
    id: int
    status: str
    issued_date: date


class PaymentCreate(SQLModel):
    invoice_id: int
    amount: float
    method: str
    paid_date: Optional[date] = None


class PaymentRead(PaymentCreate):
    id: int
    paid_date: date


class FinancialReport(SQLModel):
    total_invoiced: float
    total_paid: float
    outstanding_balance: float
    pending_invoices: int
    paid_invoices: int


class PatientReport(SQLModel):
    patient: PatientRead
    total_invoiced: float
    total_paid: float
    outstanding_balance: float
    notes_count: int


class DoctorProductivity(SQLModel):
    doctor_id: int
    doctor_name: str
    patient_count: int
    notes_authored: int
