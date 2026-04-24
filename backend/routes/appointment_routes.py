from flask import Blueprint, request, redirect, render_template, flash, session
import urllib.parse
from services.appointment_service import (
    book_appointment_request, fetch_pending_requests, fetch_ongoing_cases,
    fetch_case_history, fetch_client_cases, change_appointment_status, rate_lawyer_case
)
from services.user_service import get_lawyer_profile

appointment_bp = Blueprint('appointment', __name__)

@appointment_bp.route('/book-appointment', methods=['POST'])
def book_appointment():
    if 'client_id' not in session:
        flash('You must be logged in as a client to book an appointment.', 'error')
        return redirect('/pages/client-login.html')
        
    lawyer_id = request.form.get('lawyer_id')
    client_id = session['client_id']
    
    success, message = book_appointment_request(client_id, lawyer_id)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
        
    query_text = request.form.get('query_text', '')
    filter_gender = request.form.get('filter_gender', '')
    filter_district = request.form.get('filter_district', '')
    if query_text:
        redirect_url = '/search-lawyer?query_text=' + urllib.parse.quote_plus(query_text)
        if filter_gender: redirect_url += '&filter_gender=' + urllib.parse.quote_plus(filter_gender)
        if filter_district: redirect_url += '&filter_district=' + urllib.parse.quote_plus(filter_district)
        return redirect(redirect_url)
    return redirect('/search-lawyer')

@appointment_bp.route('/client-requests')
def client_requests():
    if 'lawyer_id' not in session:
        return redirect('/pages/lawyer-login.html')
        
    lawyer_id = session['lawyer_id']
    if 'lawyer_name' not in session:
        lawyer_prof = get_lawyer_profile(lawyer_id)
        if lawyer_prof: session['lawyer_name'] = lawyer_prof['name']
        
    appointments = fetch_pending_requests(lawyer_id)
    return render_template('pages/client-requests.html', appointments=appointments)

@appointment_bp.route('/accept-appointment/<int:appt_id>', methods=['POST'])
def accept_appointment(appt_id):
    if 'lawyer_id' not in session: 
        return redirect('/pages/lawyer-login.html')
        
    success = change_appointment_status(appt_id, session['lawyer_id'], 'In Progress')
    if success:
        flash('Appointment Accepted, marked as In Progress!', 'success')
    return redirect('/client-requests')

@appointment_bp.route('/reject-appointment/<int:appt_id>', methods=['POST'])
def reject_appointment(appt_id):
    if 'lawyer_id' not in session: 
        return redirect('/pages/lawyer-login.html')
        
    success = change_appointment_status(appt_id, session['lawyer_id'], 'Rejected')
    if success:
        flash('Appointment Rejected.', 'success')
    return redirect('/client-requests')

@appointment_bp.route('/ongoing-cases')
def ongoing_cases():
    if 'lawyer_id' not in session:
        return redirect('/pages/lawyer-login.html')
        
    lawyer_id = session['lawyer_id']
    if 'lawyer_name' not in session:
        lawyer_prof = get_lawyer_profile(lawyer_id)
        if lawyer_prof: session['lawyer_name'] = lawyer_prof['name']
        
    cases = fetch_ongoing_cases(lawyer_id)
    return render_template('pages/ongoing-cases.html', cases=cases)

@appointment_bp.route('/update-case-status/<int:appt_id>', methods=['POST'])
def update_case_status(appt_id):
    if 'lawyer_id' not in session:
        return redirect('/pages/lawyer-login.html')
        
    new_status = request.form.get('status')
    if new_status not in ['Won', 'Lost']:
        flash('Invalid status update.', 'error')
        return redirect('/ongoing-cases')
        
    success = change_appointment_status(appt_id, session['lawyer_id'], new_status)
    if success:
        flash(f'Case marked as {new_status}.', 'success')
    return redirect('/ongoing-cases')

@appointment_bp.route('/case-history')
def case_history():
    if 'lawyer_id' not in session:
        return redirect('/pages/lawyer-login.html')
        
    lawyer_id = session['lawyer_id']
    if 'lawyer_name' not in session:
        lawyer_prof = get_lawyer_profile(lawyer_id)
        if lawyer_prof: session['lawyer_name'] = lawyer_prof['name']
        
    cases = fetch_case_history(lawyer_id)
    return render_template('pages/case-history.html', cases=cases)

@appointment_bp.route('/my-cases')
def my_cases():
    if 'client_id' not in session:
        return redirect('/pages/client-login.html')
        
    cases = fetch_client_cases(session['client_id'])
    return render_template('pages/my-cases.html', cases=cases)

@appointment_bp.route('/rate-lawyer/<int:appt_id>', methods=['POST'])
def rate_lawyer(appt_id):
    if 'client_id' not in session:
        return redirect('/pages/client-login.html')
        
    rating = request.form.get('rating')
    if not rating or not rating.isdigit() or not (1 <= int(rating) <= 5):
        flash('Invalid rating submitted.', 'error')
        return redirect('/my-cases')
        
    client_id = session['client_id']
    success, message = rate_lawyer_case(appt_id, client_id, rating)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
        
    return redirect('/my-cases')
