import mysql.connector
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
from config import DB_CONFIG

def update_schema():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        print("Adding OTP columns to clients table...")
        try:
            cursor.execute("ALTER TABLE clients ADD COLUMN otp_code VARCHAR(10), ADD COLUMN otp_expiry DATETIME;")
            print("Successfully updated clients table.")
        except mysql.connector.Error as e:
            if "Duplicate column name" in str(e):
                print("Columns already exist in clients table.")
            else:
                print(f"Error updating clients table: {e}")

        print("Adding OTP columns to lawyers table...")
        try:
            cursor.execute("ALTER TABLE lawyers ADD COLUMN otp_code VARCHAR(10), ADD COLUMN otp_expiry DATETIME;")
            print("Successfully updated lawyers table.")
        except mysql.connector.Error as e:
            if "Duplicate column name" in str(e):
                print("Columns already exist in lawyers table.")
            else:
                print(f"Error updating lawyers table: {e}")

        conn.commit()
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    update_schema()
