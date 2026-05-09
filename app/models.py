"""SQLModel table definitions for the dental CRM system."""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Doctor(SQLModel, table=True):
    """Represents a dentist or specialist working at the clinic."""

    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str
    specialty: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class Patient(SQLModel, table=True):
    """Represents a patient receiving care from the clinic."""

    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str
    date_of_birth: date
    contact_phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    primary_doctor_id: Optional[int] = Field(default=None, foreign_key="doctor.id")


class MedicalNote(SQLModel, table=True):
    """Clinical notes recorded by providers during consultations."""

    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="patient.id")
    doctor_id: int = Field(foreign_key="doctor.id")
    note: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Invoice(SQLModel, table=True):
    """Invoice for treatment or services provided to a patient."""

    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="patient.id")
    description: Optional[str] = None
    amount: float
    status: str = Field(default="pending")
    issued_date: date = Field(default_factory=date.today)


class Payment(SQLModel, table=True):
    """Payment tied to an invoice."""

    id: Optional[int] = Field(default=None, primary_key=True)
    invoice_id: int = Field(foreign_key="invoice.id")
    amount: float
    paid_date: date = Field(default_factory=date.today)
    method: str = Field(default="cash")
