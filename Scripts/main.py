# Test script

from db.connector import DatabaseConnector

print("Starting DB connection process...\n")
db = DatabaseConnector()
conn, cursor = db.connect()

if cursor:
    cursor.execute("SELECT TOP 1 * FROM some_table")  # Adjust based on your DB type
    for row in cursor.fetchall():
        print(row)

db.close()
