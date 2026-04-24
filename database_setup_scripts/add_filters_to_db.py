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
    ALTER TABLE lawyers 
    ADD COLUMN gender ENUM('Male', 'Female', 'Other') DEFAULT NULL,
    ADD COLUMN district VARCHAR(100) DEFAULT NULL
    """)
    print("Columns 'gender' and 'district' added to 'lawyers' table.")
    
    conn.commit()
    cursor.close()
    conn.close()
except mysql.connector.Error as err:
    print(f"Error: {err}")
