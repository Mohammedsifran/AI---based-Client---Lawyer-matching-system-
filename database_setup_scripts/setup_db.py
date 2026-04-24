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

    # Create lawyers table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lawyers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        specialization VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    print("Table 'lawyers' created (or already exists).")

    cursor.close()
    conn.close()

except mysql.connector.Error as err:
    print(f"Error: {err}")
