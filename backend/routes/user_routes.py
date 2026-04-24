from flask import Blueprint, request, redirect, render_template, flash, session
import os
import uuid
import urllib.parse
from config import UPLOAD_FOLDER
from utils.helpers import allowed_file
from services.user_service import (
    get_lawyer_profile, update_lawyer_profile_service,
    get_client_profile, update_client_profile_service,
    save_favorite_lawyer, remove_favorite_lawyer, get_favorite_lawyers
)

user_bp = Blueprint('user', __name__)

@user_bp.route('/lawyer-profile', methods=['GET'])
def lawyer_profile():
    if 'lawyer_id' not in session:
        flash('Please login first', 'error')
        return redirect('/pages/lawyer-login.html')
        
    lawyer = get_lawyer_profile(session['lawyer_id'])
    if lawyer and 'lawyer_name' not in session:
        session['lawyer_name'] = lawyer['name']
        
    return render_template('pages/lawyer-profile.html', lawyer=lawyer)

@user_bp.route('/update-lawyer-profile', methods=['POST'])
def update_lawyer_profile():
    if 'lawyer_id' not in session:
        return redirect('/pages/lawyer-login.html')
        
    description = request.form.get('description', '')
    gender = request.form.get('gender')
    district = request.form.get('district')
    
    # Handle Profile Picture
    filename = None
    if 'profile_picture' in request.files:
        file = request.files['profile_picture']
        if file and file.filename != '' and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"lawyer_{session['lawyer_id']}_{uuid.uuid4().hex[:8]}.{ext}"
            try:
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                session['profile_picture'] = filename
            except Exception as e:
                print(f"Error saving file: {e}")
                filename = None
    
    success = update_lawyer_profile_service(session['lawyer_id'], description, gender, district, filename)
    if success:
        flash('Profile updated successfully!', 'success')
    else:
        flash('Error updating profile.', 'error')
        
    return redirect('/lawyer-profile')

@user_bp.route('/client-profile', methods=['GET'])
def client_profile():
    if 'client_id' not in session:
        flash('Please login to view your profile', 'error')
        return redirect('/pages/client-login.html')
        
    client = get_client_profile(session['client_id'])
    return render_template('pages/client-profile.html', client=client)

@user_bp.route('/update-client-profile', methods=['POST'])
def update_client_profile():
    if 'client_id' not in session:
        return redirect('/pages/client-login.html')
        
    email = request.form.get('email', '')
    phone = request.form.get('phone_number', '')
    
    filename = session.get('profile_picture')
    if 'profile_picture' in request.files:
        file = request.files['profile_picture']
        if file and file.filename != '' and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"client_{session['client_id']}_{uuid.uuid4().hex[:8]}.{ext}"
            try:
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                session['profile_picture'] = filename
            except Exception as e:
                print(f"Error saving file: {e}")
                filename = session.get('profile_picture')
                
    success = update_client_profile_service(session['client_id'], email, phone, filename)
    if success:
        flash('Profile updated successfully!', 'success')
    else:
        flash('Error updating profile. Email may already be in use.', 'error')
        
    return redirect('/client-profile')

@user_bp.route('/save-lawyer', methods=['POST'])
def save_lawyer():
    if 'client_id' not in session:
        flash('You must be logged in as a client to save a lawyer.', 'error')
        return redirect('/pages/client-login.html')
        
    lawyer_id = request.form.get('lawyer_id')
    client_id = session['client_id']
    
    result = save_favorite_lawyer(client_id, lawyer_id)
    if result == "SUCCESS":
        flash('Lawyer saved to your favorites!', 'success')
    elif result == "DUPLICATE":
        flash('This lawyer is already in your favorites.', 'error')
    else:
        flash('An error occurred while saving.', 'error')
        
    query_text = request.form.get('query_text', '')
    filter_gender = request.form.get('filter_gender', '')
    filter_district = request.form.get('filter_district', '')
    if query_text:
        redirect_url = '/search-lawyer?query_text=' + urllib.parse.quote_plus(query_text)
        if filter_gender: redirect_url += '&filter_gender=' + urllib.parse.quote_plus(filter_gender)
        if filter_district: redirect_url += '&filter_district=' + urllib.parse.quote_plus(filter_district)
        return redirect(redirect_url)
    return redirect('/search-lawyer')

@user_bp.route('/remove-lawyer', methods=['POST'])
def remove_lawyer():
    if 'client_id' not in session:
        return redirect('/pages/client-login.html')
        
    lawyer_id = request.form.get('lawyer_id')
    client_id = session['client_id']
    
    success = remove_favorite_lawyer(client_id, lawyer_id)
    if success:
        flash('Lawyer removed from favorites.', 'success')
        
    return redirect('/favorite-lawyers')

@user_bp.route('/favorite-lawyers')
def favorite_lawyers():
    if 'client_id' not in session:
        flash('Please login to view saved lawyers', 'error')
        return redirect('/pages/client-login.html')
        
    client_id = session['client_id']
    
    # Auto-patch missing client name
    if 'client_name' not in session:
        client_prof = get_client_profile(client_id)
        if client_prof: 
            session['client_name'] = client_prof['name']
            
    lawyers = get_favorite_lawyers(client_id)
    return render_template('pages/favorite-lawyers.html', lawyers=lawyers)
