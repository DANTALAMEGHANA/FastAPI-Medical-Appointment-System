# FastAPI-Medical-Appointment-System

A FastAPI-based management system for a Medicare Clinic, featuring doctor registries, appointment scheduling, and automated fee calculations.

🚀 Features
👨‍⚕️ Doctor Management
Summary Statistics: View total doctors, availability counts, most experienced doctors, and cheapest fees.

Filtering: Filter doctors by specialization, max fee, minimum experience, and availability.

Search: Keyword-based search across doctor names and specializations.

Sorting & Pagination: Sort doctors by fee, name, or experience with limit-based paging.

Management: Endpoints to add new doctors, update fees/availability, and delete doctors (safety check included for active appointments).

📅 Appointment System
Booking: Create appointments with automated fee calculations based on type and patient status.

Fee Engine Logic:

Video: 20% Discount

Emergency: 50% Surcharge

In-person: Base Fee

Senior Citizen: Additional 15% Discount

Status Management: Workflow to Confirm, Cancel, and Complete appointments.

Search & Sort: Search appointments by patient name and sort by fee or date.


⚙️ Setup and Installation
Install Dependencies:

Bash
pip install fastapi uvicorn pydantic
Run the Application:

Bash
uvicorn main:app --reload

📖 API Endpoints
Doctors
GET /doctors: Get all doctors.

GET /doctors/summary: Get clinic statistics.

GET /doctors/filter: Filter by criteria.

GET /doctors/search: Search by keyword.

GET /doctors/sort: Sort by name/fee/experience.

GET /doctors/page: Paginated doctor list.

GET /doctors/browse: Combined search, sort, and page.

POST /doctors: Add a new doctor.

PUT /doctors/{doctor_id}: Update doctor details.

DELETE /doctors/{doctor_id}: Remove a doctor.

Appointments
GET /appointments: List all appointments.

POST /appointments: Book a new appointment.

GET /appointments/search: Search by patient name.

GET /appointments/sort: Sort by fee or date.

GET /appointments/page: Paginated appointments.

GET /appointments/active: View scheduled/confirmed appointments.

POST /appointments/{id}/confirm: Set status to confirmed.

POST /appointments/{id}/cancel: Set status to cancelled (releases doctor).

POST /appointments/{id}/complete: Set status to completed.

🧪 Data Models
AppointmentRequest
patient_name: string (min 2)

doctor_id: integer (gt 0)

date: string (min 8)

reason: string (min 5)

appointment_type: string (default: 'in-person')

senior_citizen: boolean (default: false)

---

## 📂 Project Structure
```text
.
├── main.py              # Main FastAPI application code
├── requirements.txt     # List of dependencies
└── README.md            # Project documentation
