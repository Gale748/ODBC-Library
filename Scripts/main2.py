from db.connector2 import DatabaseConnector

db = DatabaseConnector()                         # prompts for DSN, username, password
conn, cursor = db.connect(max_attempts=5)        # retries on failure

if conn:
    df = db.query_dataframe("SELECT TOP 100 * FROM some_table")
    print(df.head())

db.close()
