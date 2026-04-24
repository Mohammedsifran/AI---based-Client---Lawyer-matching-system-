from models.appointment_model import (
    check_existing_appointment, create_appointment, get_pending_appointments_for_lawyer,
    get_ongoing_cases_for_lawyer, get_case_history_for_lawyer, get_cases_for_client,
    update_appointment_status, get_appointment_for_rating, rate_appointment,
    get_appointment_by_id
)
from models.user_model import update_lawyer_user_rating, get_client_by_id, get_lawyer_by_id
from services.email_service import send_new_request_notification, send_acceptance_notification, send_status_update_notification

def book_appointment_request(client_id, lawyer_id):
    existing = check_existing_appointment(client_id, lawyer_id)
    if existing:
        return False, "You already have an active appointment request with this lawyer."
    
    success = create_appointment(client_id, lawyer_id)
    if success:
        # Trigger Email Notification
        client = get_client_by_id(client_id)
        lawyer = get_lawyer_by_id(lawyer_id)
        if client and lawyer:
            send_new_request_notification(client['name'], lawyer['email'])
            
        return True, "Appointment request sent successfully! The lawyer will review it shortly."
    return False, "An error occurred while booking"

def fetch_pending_requests(lawyer_id):
    return get_pending_appointments_for_lawyer(lawyer_id)

def fetch_ongoing_cases(lawyer_id):
    return get_ongoing_cases_for_lawyer(lawyer_id)

def fetch_case_history(lawyer_id):
    return get_case_history_for_lawyer(lawyer_id)

def fetch_client_cases(client_id):
    return get_cases_for_client(client_id)

def change_appointment_status(appt_id, lawyer_id, status):
    # Pre-fetch appointment data for email context
    appt = get_appointment_by_id(appt_id)
    
    success = update_appointment_status(appt_id, lawyer_id, status)
    
    if success and appt:
        if status == 'In Progress':
            # Send Client Acceptance Notification Email
            send_acceptance_notification(appt['client_email'], appt['lawyer_name'])
        elif status in ['Won', 'Lost', 'Rejected']:
            # Send general status update
            send_status_update_notification(appt['client_email'], appt['lawyer_name'], status)
            
    return success

def rate_lawyer_case(appt_id, client_id, rating):
    appt = get_appointment_for_rating(appt_id, client_id)
    
    if not appt or appt['status'] not in ['Won', 'Lost']:
        return False, "This case cannot be rated yet."
    elif appt['client_rating'] is not None:
        return False, "You have already rated this lawyer for this case."
    
    success_rate = rate_appointment(appt_id, int(rating))
    if success_rate:
        # Update lawyer general rating
        update_lawyer_user_rating(appt['lawyer_id'])
        return True, "Thank you! Your rating has been saved."
    return False, "Error saving rating."
