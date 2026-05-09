from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from app.database import get_session
from app.main import app


def setup_test_app():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)

    def get_test_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_test_session
    return TestClient(app)


@pytest.fixture()
def client():
    client = setup_test_app()
    yield client
    app.dependency_overrides.clear()


def test_full_workflow(client: TestClient):
    doctor_payload = {
        "full_name": "Dr. Ada Lovelace",
        "specialty": "Orthodontics",
        "phone": "555-0001",
    }
    doctor = client.post("/doctors", json=doctor_payload).json()
    assert doctor["id"] == 1

    patient_payload = {
        "full_name": "Grace Hopper",
        "date_of_birth": date(1985, 1, 1).isoformat(),
        "contact_phone": "555-0022",
        "primary_doctor_id": doctor["id"],
    }
    patient = client.post("/patients", json=patient_payload).json()
    assert patient["primary_doctor_id"] == doctor["id"]

    note_payload = {
        "patient_id": patient["id"],
        "doctor_id": doctor["id"],
        "note": "Routine cleaning completed",
    }
    note = client.post("/medical-notes", json=note_payload).json()
    assert note["patient_id"] == patient["id"]

    invoice_payload = {
        "patient_id": patient["id"],
        "amount": 200.0,
        "description": "Cleaning and x-rays",
    }
    invoice = client.post("/invoices", json=invoice_payload).json()
    assert invoice["status"] == "pending"

    payment_payload = {
        "invoice_id": invoice["id"],
        "amount": 200.0,
        "method": "credit_card",
    }
    payment = client.post("/payments", json=payment_payload).json()
    assert payment["invoice_id"] == invoice["id"]

    updated_invoice = client.get("/invoices").json()[0]
    assert updated_invoice["status"] == "paid"

    financial_report = client.get("/reports/financial").json()
    assert financial_report["total_invoiced"] == pytest.approx(200.0)
    assert financial_report["outstanding_balance"] == pytest.approx(0.0)

    patient_report = client.get(f"/reports/patients/{patient['id']}").json()
    assert patient_report["notes_count"] == 1
    assert patient_report["outstanding_balance"] == pytest.approx(0.0)

    productivity = client.get("/reports/doctors/productivity").json()
    assert productivity[0]["patient_count"] == 1
    assert productivity[0]["notes_authored"] == 1
