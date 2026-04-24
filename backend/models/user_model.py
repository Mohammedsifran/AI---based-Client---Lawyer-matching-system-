from utils.db import get_db_connection
import mysql.connector

# --- CLIENT MODELS ---

def get_client_by_id(client_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM clients WHERE id = %s", (client_id,))
        client = cursor.fetchone()
        cursor.close()
        conn.close()
        return client
    return None

def get_client_by_email(email):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM clients WHERE email = %s", (email,))
        client = cursor.fetchone()
        cursor.close()
        conn.close()
        return client
    return None

def create_client(name, email, password):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            query = "INSERT INTO clients (name, email, password) VALUES (%s, %s, %s)"
            cursor.execute(query, (name, email, password))
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

def update_client_profile(client_id, email, phone, profile_picture):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            update_query = """
                UPDATE clients 
                SET profile_picture = %s, email = %s, phone_number = %s 
                WHERE id = %s
            """
            cursor.execute(update_query, (profile_picture, email, phone, client_id))
            conn.commit()
            success = True
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            conn.rollback()
            success = False
        finally:
            cursor.close()
            conn.close()
        return success
    return False

# --- LAWYER MODELS ---

def get_lawyer_by_id(lawyer_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM lawyers WHERE id = %s", (lawyer_id,))
        lawyer = cursor.fetchone()
        cursor.close()
        conn.close()
        return lawyer
    return None

def get_lawyer_by_email(email):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM lawyers WHERE email = %s", (email,))
        lawyer = cursor.fetchone()
        cursor.close()
        conn.close()
        return lawyer
    return None

def create_lawyer(name, email, password, specialization, gender, district):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            query = "INSERT INTO lawyers (name, email, password, specialization, gender, district) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (name, email, password, specialization, gender, district))
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

def update_lawyer_profile_full(lawyer_id, description, specialization, experience, juniors_count, cases_count, ranking_score, profile_picture, gender, district):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            if profile_picture:
                update_query = """
                    UPDATE lawyers 
                    SET description = %s, specialization = %s, 
                        experience = %s, juniors_count = %s, cases_count = %s, ranking_score = %s, profile_picture = %s, gender = %s, district = %s
                    WHERE id = %s
                """
                cursor.execute(update_query, (
                    description, specialization, experience, juniors_count, cases_count, ranking_score, profile_picture, gender, district, lawyer_id
                ))
            else:
                update_query = """
                    UPDATE lawyers 
                    SET description = %s, specialization = %s, 
                        experience = %s, juniors_count = %s, cases_count = %s, ranking_score = %s, gender = %s, district = %s
                    WHERE id = %s
                """
                cursor.execute(update_query, (
                    description, specialization, experience, juniors_count, cases_count, ranking_score, gender, district, lawyer_id
                ))
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

def search_lawyers(specialization, gender=None, district=None, limit=5):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT * FROM lawyers WHERE specialization = %s AND is_approved = 1"
        params = [specialization]
        
        if gender:
            sql += " AND gender = %s"
            params.append(gender)
        if district:
            sql += " AND district = %s"
            params.append(district)
            
        sql += " ORDER BY ranking_score DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(sql, tuple(params))
        lawyers = cursor.fetchall()
        cursor.close()
        conn.close()
        return lawyers
    return []

def get_lawyer_user_rating(lawyer_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT user_rating FROM lawyers WHERE id = %s", (lawyer_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return row['user_rating'] if row and row['user_rating'] else 0.0
    return 0.0

def update_lawyer_user_rating(lawyer_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        # Update user_rating first
        cursor.execute('''
            UPDATE lawyers 
            SET user_rating = (
                SELECT COALESCE(AVG(client_rating) * 2, 0) 
                FROM appointments 
                WHERE lawyer_id = %s AND client_rating IS NOT NULL
            )
            WHERE id = %s
        ''', (lawyer_id, lawyer_id))
        
        # Now fetch the user and recalculate ranking_score
        cursor.execute("SELECT experience, juniors_count, cases_count, user_rating FROM lawyers WHERE id = %s", (lawyer_id,))
        lawyer = cursor.fetchone()
        if lawyer:
            # Experience Points
            exp = lawyer['experience'] or 0
            if exp < 5: exp_pts = 2.5
            elif 5 <= exp <= 10: exp_pts = 5.0
            elif 10 < exp <= 17: exp_pts = 7.5
            else: exp_pts = 10.0
            
            # Juniors Count Points
            jun = lawyer['juniors_count'] or 0
            if jun < 5: jun_pts = 2.5
            elif 5 <= jun <= 8: jun_pts = 5.0
            elif 8 < jun <= 12: jun_pts = 7.5
            else: jun_pts = 10.0
            
            # Cases Count Points
            cases = lawyer['cases_count'] or 0
            if cases < 20: case_pts = 2.5
            elif 20 <= cases <= 50: case_pts = 5.0
            elif 50 < cases <= 80: case_pts = 7.5
            else: case_pts = 10.0
            
            new_score = (exp_pts + jun_pts + case_pts + lawyer['user_rating']) / 4.0
            
            # In update query, we need standard cursor to commit changes without returning dict
            cursor.close()
            cursor = conn.cursor()
            cursor.execute("UPDATE lawyers SET ranking_score = %s WHERE id = %s", (round(new_score, 2), lawyer_id))
            
        conn.commit()
        cursor.close()
        conn.close()

# --- ADMIN UPDATES ---
def update_user_details(user_id, role, new_email, new_name, new_specialization=None):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        success = True
        try:
            if role == 'Lawyer':
                if new_specialization:
                    cursor.execute("UPDATE lawyers SET email = %s, name = %s, specialization = %s WHERE id = %s", (new_email, new_name, new_specialization, user_id))
                else:
                    cursor.execute("UPDATE lawyers SET email = %s, name = %s WHERE id = %s", (new_email, new_name, user_id))
            elif role == 'Client':
                cursor.execute("UPDATE clients SET email = %s, name = %s WHERE id = %s", (new_email, new_name, user_id))
            conn.commit()
        except mysql.connector.Error as err:
            success = False
        finally:
            cursor.close()
            conn.close()
        return success
    return False
