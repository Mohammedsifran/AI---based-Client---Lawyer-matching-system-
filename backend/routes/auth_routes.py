from flask import Blueprint, request, redirect, flash, session
from services.auth_service import authenticate_client, authenticate_lawyer, authenticate_admin, register_client, register_lawyer, generate_and_send_otp, verify_otp, reset_password

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/client-login', methods=['POST'])
def client_login():
    email = request.form.get('email')
    password = request.form.get('password')

    # 1. Check if it's an Admin
    admin = authenticate_admin(email, password)
    if admin:
        return redirect('/pages/admin-dashboard.html')

    # 2. Check if it's a Client
    user = authenticate_client(email, password)
    if user:
        session['client_id'] = user['id']
        session['client_name'] = user['name']
        session['profile_picture'] = user.get('profile_picture')
        return redirect('/search-lawyer')
    else:
        flash('Invalid email or password', 'error')
        return redirect('/pages/client-login.html')

@auth_bp.route('/lawyer-login', methods=['POST'])
def lawyer_login():
    email = request.form.get('email')
    password = request.form.get('password')

    # 1. Check if it's an Admin
    admin = authenticate_admin(email, password)
    if admin:
        return redirect('/pages/admin-dashboard.html')

    # 2. Check if it's a Lawyer
    user = authenticate_lawyer(email, password)
    if user:
        if user['is_approved'] == 0:
            flash('Your account is pending approval by the administrator.', 'error')
            return redirect('/pages/lawyer-login.html')
        
        session['lawyer_id'] = user['id']
        session['lawyer_name'] = user['name']
        session['profile_picture'] = user.get('profile_picture')
        return redirect('/lawyer-profile')
    else:
        flash('Invalid email or password', 'error')
        return redirect('/pages/lawyer-login.html')

@auth_bp.route('/admin-login', methods=['POST'])
def admin_login():
    username = request.form.get('username')
    password = request.form.get('password')

    admin = authenticate_admin(username, password)
    if admin:
        return redirect('/pages/admin-dashboard.html')
    else:
        flash('Invalid username or password', 'error')
        return redirect('/pages/admin-login.html')

@auth_bp.route('/lawyer-register', methods=['POST'])
def lawyer_register():
    fullname = request.form.get('fullname')
    email = request.form.get('email')
    specialization = request.form.get('specialization')
    gender = request.form.get('gender')
    district = request.form.get('district')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm-password')

    if password != confirm_password:
        flash('Passwords do not match', 'error')
        return redirect('/pages/lawyer-register.html')

    success, message = register_lawyer(fullname, email, password, specialization, gender, district)
    if success:
        flash(message, 'success')
        return redirect('/pages/lawyer-login.html')
    else:
        flash(message, 'error')
        return redirect('/pages/lawyer-register.html')

@auth_bp.route('/client-register', methods=['POST'])
def client_register():
    fullname = request.form.get('fullname')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm-password')

    if password != confirm_password:
        flash('Passwords do not match', 'error')
        return redirect('/pages/client-register.html')

    success, message = register_client(fullname, email, password)
    if success:
        flash(message, 'success')
        return redirect('/pages/client-login.html')
    else:
        flash(message, 'error')
        return redirect('/pages/client-register.html')

@auth_bp.route('/send-otp', methods=['POST'])
def send_otp():
    email = request.form.get('email')
    user_role = request.form.get('user_role')
    
    success, message = generate_and_send_otp(email, user_role)
    if success:
        session['reset_email'] = email
        session['reset_role'] = user_role
        flash(message, 'success')
        return redirect('/pages/verify-otp.html')
    else:
        flash(message, 'error')
        return redirect('/pages/forgot-password.html')

@auth_bp.route('/verify-otp', methods=['POST'])
def handle_verify_otp():
    email = session.get('reset_email')
    user_role = session.get('reset_role')
    entered_otp = request.form.get('otp_code')
    
    if not email or not user_role:
        flash("Session expired. Please try again.", "error")
        return redirect('/pages/forgot-password.html')

    success, message = verify_otp(email, user_role, entered_otp)
    if success:
        session['otp_verified'] = True
        flash(message, 'success')
        return redirect('/pages/reset-password.html')
    else:
        flash(message, 'error')
        return redirect('/pages/verify-otp.html')

@auth_bp.route('/reset-password', methods=['POST'])
def handle_reset_password():
    email = session.get('reset_email')
    user_role = session.get('reset_role')
    is_verified = session.get('otp_verified')
    
    if not email or not is_verified:
        flash("Unauthorized password reset request.", "error")
        return redirect('/pages/forgot-password.html')
        
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    
    if password != confirm_password:
        flash("Passwords do not match.", "error")
        return redirect('/pages/reset-password.html')
        
    success, message = reset_password(email, user_role, password)
    if success:
        # Clear reset session payload
        session.pop('reset_email', None)
        session.pop('reset_role', None)
        session.pop('otp_verified', None)
        
        flash(message, 'success')
        if user_role == 'Client':
            return redirect('/pages/client-login.html')
        else:
            return redirect('/pages/lawyer-login.html')
    else:
        flash(message, 'error')
        return redirect('/pages/reset-password.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')
