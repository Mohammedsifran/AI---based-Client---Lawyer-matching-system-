from models.user_model import get_client_by_email, create_client, get_lawyer_by_email, create_lawyer
from models.admin_model import get_admin
from utils.db import get_db_connection
import random
from datetime import datetime, timedelta
import mysql.connector
from services.email_service import send_otp_email

def authenticate_client(email, password):
    client = get_client_by_email(email)
    if client and client['password'] == password:
        return client
    return None

def authenticate_lawyer(email, password):
    lawyer = get_lawyer_by_email(email)
    if lawyer and lawyer['password'] == password:
        return lawyer
    return None

def authenticate_admin(username, password):
    admin = get_admin(username, password)
    return admin

def register_client(name, email, password):
    # Check if exists
    if get_client_by_email(email):
        return False, "Email already registered"
    
    success = create_client(name, email, password)
    if success:
        return True, "Registration successful! Please login."
    return False, "An error occurred during registration"

def register_lawyer(name, email, password, specialization, gender, district):
    # Check if exists
    if get_lawyer_by_email(email):
        return False, "Email already registered"
    
    success = create_lawyer(name, email, password, specialization, gender, district)
    if success:
        return True, "Registration successful! Please login."
    return False, "An error occurred during registration"

def generate_and_send_otp(email, user_role):
    # Determine table
    table = 'clients' if user_role == 'Client' else 'lawyers'
    
    # Check user exists
    user = get_client_by_email(email) if user_role == 'Client' else get_lawyer_by_email(email)
    if not user:
        return False, "Account with this email does not exist."
    
    otp = str(random.randint(100000, 999999))
    expiry = datetime.now() + timedelta(minutes=15)
    
    conn = get_db_connection()
    if not conn:
        return False, "Database connection error."
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE {table} SET otp_code = %s, otp_expiry = %s WHERE email = %s", (otp, expiry, email))
        conn.commit()
    except mysql.connector.Error as err:
        return False, f"Database error: {err}"
    finally:
        if cursor:
            cursor.close()
        conn.close()
        
    # Send email
    success = send_otp_email(email, otp)
    if success:
        return True, "OTP sent successfully."
    else:
        return False, "Failed to send email. Check backend logs."

def verify_otp(email, user_role, entered_otp):
    table = 'clients' if user_role == 'Client' else 'lawyers'
    conn = get_db_connection()
    if not conn:
        return False, "Database connection error."
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT otp_code, otp_expiry FROM {table} WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if not user or not user.get('otp_code'):
            return False, "OTP not found."
            
        if user['otp_code'] != entered_otp:
            return False, "Invalid OTP."
            
        if user['otp_expiry'] < datetime.now():
            return False, "OTP has expired."
            
        return True, "OTP verified successfully."
    except mysql.connector.Error as err:
        return False, f"Database error: {err}"
    finally:
        if cursor:
            cursor.close()
        conn.close()

def reset_password(email, user_role, new_password):
    table = 'clients' if user_role == 'Client' else 'lawyers'
    conn = get_db_connection()
    if not conn:
        return False, "Database connection error."
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE {table} SET password = %s, otp_code = NULL, otp_expiry = NULL WHERE email = %s", (new_password, email))
        conn.commit()
        return True, "Password reset successfully."
    except mysql.connector.Error as err:
        return False, f"Database error: {err}"
    finally:
        if cursor:
            cursor.close()
        conn.close()
