import mysql.connector

config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'matching'
}

try:
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    cursor.execute("""
    ALTER TABLE clients 
    ADD COLUMN phone_number VARCHAR(20) DEFAULT NULL
    """)
    print("Column 'phone_number' added to 'clients' table.")
    
    conn.commit()
    cursor.close()
    conn.close()
except mysql.connector.Error as err:
    print(f"Error: {err}")
