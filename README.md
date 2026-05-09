# Codex-playground

Dental CRM system built with FastAPI and SQLModel for managing clinical notes, patients, and finances.

## Features

- Manage doctors and patients, including assignment of a primary doctor per patient
- Record medical notes authored by providers
- Track invoices and payments with automatic invoice status updates
- Generate financial, patient, and doctor productivity reports

## Getting started

1. Create a virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt -r requirements-dev.txt
   ```

2. Run the FastAPI application:

   ```bash
   uvicorn app.main:app --reload
   ```

   The interactive API documentation is available at `http://127.0.0.1:8000/docs`.

3. Execute the test suite:

   ```bash
   pytest
   ```

## Project structure

- `app/` – FastAPI application, database models, and CRUD helpers
- `tests/` – Automated tests covering the main workflow
- `requirements*.txt` – Runtime and development dependencies
