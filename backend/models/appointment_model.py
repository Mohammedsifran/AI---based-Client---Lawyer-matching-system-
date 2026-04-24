from utils.db import get_db_connection
import mysql.connector

# --- APPOINTMENTS ---

def check_existing_appointment(client_id, lawyer_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM appointments WHERE client_id = %s AND lawyer_id = %s AND status != 'Rejected'", (client_id, lawyer_id))
        existing = cursor.fetchone()
        cursor.close()
        conn.close()
        return existing
    return None

def get_appointment_by_id(appt_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT a.*, c.name as client_name, c.email as client_email, l.name as lawyer_name, l.email as lawyer_email
            FROM appointments a
            JOIN clients c ON a.client_id = c.id
            JOIN lawyers l ON a.lawyer_id = l.id
            WHERE a.id = %s
        ''', (appt_id,))
        appt = cursor.fetchone()
        cursor.close()
        conn.close()
        return appt
    return None

def create_appointment(client_id, lawyer_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO appointments (client_id, lawyer_id) VALUES (%s, %s)", (client_id, lawyer_id))
            conn.commit()
            success = True
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            success = False
        finally:
            cursor.close()
            conn.close()
        return success
    return False

def get_pending_appointments_for_lawyer(lawyer_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT a.*, c.name as client_name, c.email as client_email, c.phone_number as client_phone 
            FROM appointments a
            JOIN clients c ON a.client_id = c.id
            WHERE a.lawyer_id = %s AND a.status = 'Pending'
            ORDER BY a.created_at DESC
        ''', (lawyer_id,))
        appointments = cursor.fetchall()
        cursor.close()
        conn.close()
        return appointments
    return []

def get_ongoing_cases_for_lawyer(lawyer_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT a.*, c.name as client_name, c.email as client_email, c.phone_number as client_phone 
            FROM appointments a
            JOIN clients c ON a.client_id = c.id
            WHERE a.lawyer_id = %s AND a.status = 'In Progress'
            ORDER BY a.created_at DESC
        ''', (lawyer_id,))
        cases = cursor.fetchall()
        cursor.close()
        conn.close()
        return cases
    return []

def get_case_history_for_lawyer(lawyer_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT a.*, c.name as client_name, c.email as client_email, c.phone_number as client_phone 
            FROM appointments a
            JOIN clients c ON a.client_id = c.id
            WHERE a.lawyer_id = %s AND a.status IN ('Won', 'Lost', 'Rejected')
            ORDER BY a.created_at DESC
        ''', (lawyer_id,))
        cases = cursor.fetchall()
        cursor.close()
        conn.close()
        return cases
    return []

def get_cases_for_client(client_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT a.*, l.name as lawyer_name, l.specialization, l.email as lawyer_email
            FROM appointments a
            JOIN lawyers l ON a.lawyer_id = l.id
            WHERE a.client_id = %s
            ORDER BY a.created_at DESC
        ''', (client_id,))
        cases = cursor.fetchall()
        cursor.close()
        conn.close()
        return cases
    return []

def update_appointment_status(appt_id, lawyer_id, status):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE appointments SET status = %s WHERE id = %s AND lawyer_id = %s", (status, appt_id, lawyer_id))
            conn.commit()
            success = True
        except mysql.connector.Error as err:
            success = False
        finally:
            cursor.close()
            conn.close()
        return success
    return False

def get_appointment_for_rating(appt_id, client_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT lawyer_id, status, client_rating FROM appointments WHERE id = %s AND client_id = %s", (appt_id, client_id))
        appt = cursor.fetchone()
        cursor.close()
        conn.close()
        return appt
    return None

def rate_appointment(appt_id, rating):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE appointments SET client_rating = %s WHERE id = %s", (rating, appt_id))
            conn.commit()
            success = True
        except mysql.connector.Error as err:
            success = False
        finally:
            cursor.close()
            conn.close()
        return success
    return False

# --- SAVED LAWYERS ---

def save_lawyer_for_client(client_id, lawyer_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO saved_lawyers (client_id, lawyer_id) VALUES (%s, %s)", (client_id, lawyer_id))
            conn.commit()
            return "SUCCESS"
        except mysql.connector.Error as err:
            if err.errno == 1062: # Duplicate entry
                return "DUPLICATE"
            return "ERROR"
        finally:
            cursor.close()
            conn.close()
    return "ERROR"

def remove_saved_lawyer(client_id, lawyer_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM saved_lawyers WHERE client_id = %s AND lawyer_id = %s", (client_id, lawyer_id))
            conn.commit()
            success = True
        except mysql.connector.Error as err:
            success = False
        finally:
            cursor.close()
            conn.close()
        return success
    return False

def get_saved_lawyers_for_client(client_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT l.* 
            FROM lawyers l
            JOIN saved_lawyers sl ON l.id = sl.lawyer_id
            WHERE sl.client_id = %s
            ORDER BY sl.created_at DESC
        ''', (client_id,))
        lawyers = cursor.fetchall()
        cursor.close()
        conn.close()
        return lawyers
    return []
