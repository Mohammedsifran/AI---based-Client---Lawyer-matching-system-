import mysql.connector

config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'matching'
}

try:
    conn = mysql.connector.connect(**config)
    print("SUCCESS: Connected to the database 'matching'")
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    print("Tables in database:")
    for (table_name,) in cursor:
        print(f"- {table_name}")
    cursor.close()
    conn.close()
except mysql.connector.Error as err:
    print(f"FAILED: {err}")
