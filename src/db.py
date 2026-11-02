import os 
from dotenv import load_dotenv
import psycopg2


load_dotenv()

def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    return conn

if __name__ == "__main__":
    try:
        connection = get_db_connection()
        cur = connection.cursor()
        cur.execute("SELECT version();")
        db_version = cur.fetchone()[0]
        print("Connected successfully!")
        print(f"PostgreSQL Version: {db_version}")
        cur.close()
        connection.close()
    except Exception as e:
        print(f"Connection failed: {e}")