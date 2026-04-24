from utils.db import get_db_connection

def get_admin(username, password):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admins WHERE username = %s AND password = %s", (username, password))
        admin = cursor.fetchone()
        cursor.close()
        conn.close()
        return admin
    return None

def get_lawyer_count():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as count FROM lawyers")
        count = cursor.fetchone()['count']
        cursor.close()
        conn.close()
        return count
    return 0

def get_client_count():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as count FROM clients")
        count = cursor.fetchone()['count']
        cursor.close()
        conn.close()
        return count
    return 0

def get_pending_lawyers():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, email, specialization, created_at FROM lawyers WHERE is_approved = 0 ORDER BY created_at DESC")
        pending_lawyers = cursor.fetchall()
        cursor.close()
        conn.close()
        return pending_lawyers
    return []

def get_all_users_for_admin():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, email, specialization, 'Lawyer' as role FROM lawyers")
        all_lawyers = cursor.fetchall()
        cursor.execute("SELECT id, name, email, NULL as specialization, 'Client' as role FROM clients")
        all_clients = cursor.fetchall()
        all_users = all_lawyers + all_clients
        cursor.close()
        conn.close()
        return all_users, all_lawyers, all_clients
    return [], [], []

def approve_lawyer_account(lawyer_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE lawyers SET is_approved = 1 WHERE id = %s", (lawyer_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    return False
