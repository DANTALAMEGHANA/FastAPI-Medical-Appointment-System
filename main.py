from fastapi import FastAPI,Query
from pydantic import BaseModel, Field
from fastapi import Response, status

app = FastAPI(title="Medical Appointment System")

@app.get('/')
def home():
    return {'message': 'Welcome to our Medicare Clinic'}


# Doctors Data
doctors = [
    {"id": 1, "name": "Dr. Ravi Kumar", "specialization": "Cardiologist",   "fee": 500, "experience_years": 10, "is_available": True},
    {"id": 2, "name": "Dr. Anjali Mehta", "specialization": "Dermatologist", "fee": 400, "experience_years": 7,  "is_available": True},
    {"id": 3, "name": "Dr. Suresh Reddy", "specialization": "Pediatrician",  "fee": 300, "experience_years": 5,  "is_available": False},
    {"id": 4, "name": "Dr. Priya Sharma", "specialization": "General",       "fee": 200, "experience_years": 4,  "is_available": True},
    {"id": 5, "name": "Dr. Arjun Patel", "specialization": "Cardiologist",   "fee": 600, "experience_years": 12, "is_available": False},
    {"id": 6, "name": "Dr. Neha Singh", "specialization": "Dermatologist",   "fee": 450, "experience_years": 8,  "is_available": True},
]

# DAY 1-------------------------------------------------------------------------------------------------------------------------------------------------------

#  Summary FIRST
@app.get('/doctors/summary')
def doctors_summary():
    total = len(doctors)
    available_count = len([d for d in doctors if d["is_available"]])
    most_experienced = max(doctors, key=lambda d: d["experience_years"])
    cheapest_fee = min(d["fee"] for d in doctors)

    specialization_count = {}
    for d in doctors:
        spec = d["specialization"]
        specialization_count[spec] = specialization_count.get(spec, 0) + 1

    return {
        "total_doctors": total,
        "available_count": available_count,
        "most_experienced_doctor": most_experienced["name"],
        "cheapest_consultation_fee": cheapest_fee,
        "specialization_count": specialization_count
    }


#  Get All Doctors
@app.get('/doctors')
def get_doctors():
    available_count = len([d for d in doctors if d["is_available"]])

    return {
        "total_doctors": len(doctors),
        "available_count": available_count,
        "doctors": doctors
    }



# Appointments
appointments = []
appt_counter = 1

@app.get('/appointments')
def get_appointments():
    return {
        "total_appointments": len(appointments),
        "appointments": appointments
    }


# DAY 2---------------------------------------------------------------------------------------------------------------------------------------------------------


class AppointmentRequest(BaseModel):
    patient_name: str = Field(..., min_length=2)
    doctor_id: int = Field(..., gt=0)
    date: str = Field(..., min_length=8)
    reason: str = Field(..., min_length=5)
    appointment_type: str = "in-person"
    senior_citizen: bool = False

# Find Doctor
def find_doctor(doctor_id: int):
    for doctor in doctors:
        if doctor["id"] == doctor_id:
            return doctor
    return None

# Calculate Fee
def calculate_fee(base_fee: int, appointment_type: str, senior_citizen: bool):
    # Step 1: Apply appointment type pricing
    if appointment_type == "video":
        fee = base_fee * 0.8
    elif appointment_type == "emergency":
        fee = base_fee * 1.5
    else:  # in-person
        fee = base_fee

    original_fee = int(fee)

    # Step 2: Apply senior citizen discount (15%)
    if senior_citizen:
        fee = fee * 0.85

    discounted_fee = int(fee)

    return original_fee, discounted_fee
    
# DAY 2,3------------------------------------------------------------------------------------------------------------------------------------------------------------
# POST Appointments


@app.post('/appointments')
def book_appointment(data: AppointmentRequest, response: Response):
    global appt_counter

    # Step 1: Find doctor
    doctor = find_doctor(data.doctor_id)
    if not doctor:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Doctor not found"}

    # Step 2: Check availability
    if not doctor["is_available"]:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": f"{doctor['name']} is not available"}
    
    doctor["is_available"] = False
    
    # step 3: Get both fees
    original_fee, final_fee = calculate_fee(
        doctor["fee"],
        data.appointment_type,
        data.senior_citizen
    )

   

    # Step 4: Create appointment
    appointment = {
        "appointment_id": appt_counter,
        "patient": data.patient_name,
        "doctor_id": data.doctor_id,  
        "doctor_name": doctor["name"],
        "date": data.date,
        "appointment_type": data.appointment_type,
        "senior_citizen": data.senior_citizen,
        "original_fee": original_fee,
        "final_fee": final_fee,
        "status": "scheduled"
    }

    appointments.append(appointment)
    appt_counter += 1

    return {
        "message": "Appointment booked successfully",
        "appointment": appointment
    }

# Helper Function-------------------------------------------------------------------------------------------------------------
def filter_doctors_logic(
    specialization=None,
    max_fee=None,
    min_experience=None,
    is_available=None
):
    result = doctors

    if specialization is not None:
        result = [d for d in result if d["specialization"].lower() == specialization.lower()]

    if max_fee is not None:
        result = [d for d in result if d["fee"] <= max_fee]

    if min_experience is not None:
        result = [d for d in result if d["experience_years"] >= min_experience]

    if is_available is not None:
        result = [d for d in result if d["is_available"] == is_available]

    return result

# GET Doctor

@app.get('/doctors/filter')
def filter_doctors(
    specialization: str = Query(None),
    max_fee: int = Query(None),
    min_experience: int = Query(None),
    is_available: bool = Query(None),
):
    result = filter_doctors_logic(
        specialization,
        max_fee,
        min_experience,
        is_available
    )

    return {
        "filters": {
            "specialization": specialization,
            "max_fee": max_fee,
            "min_experience": min_experience,
            "is_available": is_available
        },
        "total_found": len(result),
        "doctors": result
    }



# DAY 4----------------------------------------------------------------------------------------------------------------------------------------------------------

# New Doctor


class NewDoctor(BaseModel):
    name: str = Field(..., min_length=2)
    specialization: str = Field(..., min_length=2)
    fee: int = Field(..., gt=0)
    experience_years: int = Field(..., gt=0)
    is_available: bool = True

#   POST Doctors


@app.post('/doctors')
def add_doctor(new_doc: NewDoctor, response: Response):
    # Check duplicate name
    existing_names = [d["name"].lower() for d in doctors]

    if new_doc.name.lower() in existing_names:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "Doctor with this name already exists"}

    # Generate new ID
    next_id = max(d["id"] for d in doctors) + 1

    doctor = {
        "id": next_id,
        "name": new_doc.name,
        "specialization": new_doc.specialization,
        "fee": new_doc.fee,
        "experience_years": new_doc.experience_years,
        "is_available": new_doc.is_available
    }

    doctors.append(doctor)

    response.status_code = status.HTTP_201_CREATED

    return {
        "message": "Doctor added successfully",
        "doctor": doctor
    }  

# PUT Doctors


@app.put('/doctors/{doctor_id}')
def update_doctor(
    doctor_id: int,
    response: Response,
    fee: int = Query(None),
    is_available: bool = Query(None),
):
    # Find doctor
    doctor = find_doctor(doctor_id)

    if not doctor:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Doctor not found"}

    # Apply updates only if provided
    if fee is not None:
        doctor["fee"] = fee

    if is_available is not None:
        doctor["is_available"] = is_available

    return {
        "message": "Doctor updated successfully",
        "doctor": doctor
    }

# DELETE Doctor

@app.delete('/doctors/{doctor_id}')
def delete_doctor(doctor_id: int, response: Response):
    # Step 1: Find doctor
    doctor = find_doctor(doctor_id)

    if not doctor:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Doctor not found"}

    # Step 2: Check active appointments
    for appt in appointments:
        if (
            appt["doctor_id"] == doctor["id"]
            and appt["status"] == "scheduled"
        ):
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                "error": f"{doctor['name']} has active appointments and cannot be deleted"
            }

    # Step 3: Delete doctor
    doctors.remove(doctor)

    return {
        "message": f"{doctor['name']} deleted successfully"
    }

# DAY 5-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# HELPER Function
def find_appointment(appointment_id: int):
    for appt in appointments:
        if appt["appointment_id"] == appointment_id:
            return appt
    return None

# GET Search appointments

@app.get('/appointments/search')
def search_appointments(
    patient_name: str = Query(..., min_length=1)
):
    results = [
        a for a in appointments
        if patient_name.lower() in a["patient"].lower()
    ]

    if not results:
        return {
            "message": f"No appointments found for: '{patient_name}'",
            "total_found": 0,
            "appointments": []
        }

    return {
        "patient_name": patient_name,
        "total_found": len(results),
        "appointments": results
    }

# GET SORT

@app.get('/appointments/sort')
def sort_appointments(
    sort_by: str = Query('fee', description="fee or date"),
    order: str = Query('asc', description="asc or desc")
):
    # Validate
    if sort_by not in ['fee', 'date']:
        return {"error": "sort_by must be 'fee' or 'date'"}

    if order not in ['asc', 'desc']:
        return {"error": "order must be 'asc' or 'desc'"}

    reverse = (order == 'desc')

    # Map fee → final_fee
    key_field = "final_fee" if sort_by == "fee" else "date"

    sorted_list = sorted(
        appointments,
        key=lambda a: a[key_field],
        reverse=reverse
    )

    return {
        "sort_by": sort_by,
        "order": order,
        "total": len(sorted_list),
        "appointments": sorted_list
    }

# GET Appointments Page

@app.get('/appointments/page')
def get_appointments_page(
    page: int = Query(1, ge=1),
    limit: int = Query(3, ge=1, le=20),
):
    start = (page - 1) * limit
    end = start + limit

    paged = appointments[start:end]

    return {
        "page": page,
        "limit": limit,
        "total_appointments": len(appointments),
        "total_pages": -(-len(appointments) // limit),
        "appointments": paged
    }

# GET Active Appointments 
@app.get('/appointments/active')
def get_active_appointments():
    active = [
        a for a in appointments
        if a["status"] in ["scheduled", "confirmed"]
    ]

    return {
        "total_active": len(active),
        "appointments": active
    }

# GET Appointments by doctor id
@app.get('/appointments/by-doctor/{doctor_id}')
def get_appointments_by_doctor(doctor_id: int, response: Response):
    doctor = find_doctor(doctor_id)

    if not doctor:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Doctor not found"}

    result = [
        a for a in appointments
        if a["doctor_id"] == doctor_id
    ]

    return {
        "doctor_id": doctor_id,
        "doctor_name": doctor["name"],
        "total_appointments": len(result),
        "appointments": result
    }

# POST Appointments Confirm

@app.post('/appointments/{appointment_id}/confirm')
def confirm_appointment(appointment_id: int, response: Response):
    appt = find_appointment(appointment_id)

    if not appt:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Appointment not found"}

    if appt["status"] != "scheduled":
        return {"error": f"Cannot confirm a {appt['status']} appointment"}

    appt["status"] = "confirmed"

    return {
        "message": "Appointment confirmed",
        "appointment": appt
    }

# POST Appointments Cancel
@app.post('/appointments/{appointment_id}/cancel')
def cancel_appointment(appointment_id: int, response: Response):
    appt = find_appointment(appointment_id)

    if not appt:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Appointment not found"}

    if appt["status"] == "cancelled":
        return {"error": "Appointment already cancelled"}

    # Change status
    appt["status"] = "cancelled"

    # Doctor update
    for doctor in doctors:
        if doctor["id"] == appt["doctor_id"]:
            doctor["is_available"] = True
            break

    return {
        "message": "Appointment cancelled",
        "appointment": appt
    }

# POST Appointments complete

@app.post('/appointments/{appointment_id}/complete')
def complete_appointment(appointment_id: int, response: Response):
    appt = find_appointment(appointment_id)

    if not appt:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Appointment not found"}

    if appt["status"] == "completed":
        return {"error": "Appointment already completed"}

    if appt["status"] == "cancelled":
        return {"error": "Cannot complete a cancelled appointment"}

    appt["status"] = "completed"

    return {
        "message": "Appointment completed",
        "appointment": appt
    }

# DAY 6------------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.get('/doctors/search')
def search_doctors(
    keyword: str = Query(..., min_length=1)
):
    results = [
        d for d in doctors
        if keyword.lower() in d["name"].lower()
        or keyword.lower() in d["specialization"].lower()
    ]

    if not results:
        return {
            "message": f"No doctors found for keyword: '{keyword}'",
            "total_found": 0,
            "doctors": []
        }

    return {
        "keyword": keyword,
        "total_found": len(results),
        "doctors": results
    }

# GET Doctors Sort

@app.get('/doctors/sort')
def sort_doctors(
    sort_by: str = Query('fee', description="fee | name | experience_years"),
    order: str = Query('asc', description="asc | desc")
):
    # Validate sort_by
    if sort_by not in ['fee', 'name', 'experience_years']:
        return {"error": "sort_by must be 'fee', 'name', or 'experience_years'"}

    # Validate order
    if order not in ['asc', 'desc']:
        return {"error": "order must be 'asc' or 'desc'"}

    # Sorting logic
    reverse = (order == 'desc')

    sorted_list = sorted(
        doctors,
        key=lambda d: d[sort_by],
        reverse=reverse
    )

    return {
        "sort_by": sort_by,
        "order": order,
        "total": len(sorted_list),
        "doctors": sorted_list
    }

# GET Doctors
@app.get('/doctors/page')
def get_doctors_page(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(3, ge=1, le=20, description="Items per page"),
):
    start = (page - 1) * limit
    end = start + limit

    paged = doctors[start:end]

    return {
        "page": page,
        "limit": limit,
        "total_doctors": len(doctors),
        "total_pages": -(-len(doctors) // limit),  # ceiling division
        "doctors": paged
    }

# GET Doctors Browse- DAY 3,6

@app.get('/doctors/browse')
def browse_doctors(
    keyword: str = Query(None),
    sort_by: str = Query('fee'),
    order: str = Query('asc'),
    page: int = Query(1, ge=1),
    limit: int = Query(4, ge=1, le=20),
):
    # Step 1: Search (filter)
    result = doctors

    if keyword:
        result = [
            d for d in result
            if keyword.lower() in d["name"].lower()
            or keyword.lower() in d["specialization"].lower()
        ]

    # Step 2: Sort (validation)
    if sort_by not in ['fee', 'name', 'experience_years']:
        return {"error": "sort_by must be 'fee', 'name', or 'experience_years'"}

    if order not in ['asc', 'desc']:
        return {"error": "order must be 'asc' or 'desc'"}

    result = sorted(
        result,
        key=lambda d: d[sort_by],
        reverse=(order == 'desc')
    )

    # Step 3: Pagination
    total = len(result)
    start = (page - 1) * limit
    paged = result[start:start + limit]

    return {
        "filters": {
            "keyword": keyword,
            "sort_by": sort_by,
            "order": order,
            "page": page,
            "limit": limit
        },
        "total_found": total,
        "total_pages": -(-total // limit),
        "doctors": paged
    }

#  GET Doctor by ID 
@app.get('/doctors/{doctor_id}')
def get_doctor(doctor_id: int):
    for doctor in doctors:
        if doctor["id"] == doctor_id:
            return {"doctor": doctor}
    
    return {"error": "Doctor not found"}