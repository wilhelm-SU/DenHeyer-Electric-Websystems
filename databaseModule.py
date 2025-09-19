from dotenv import load_dotenv
import psycopg2, os

# Database credentials
load_dotenv()
DB_CONFIG = {
    'host': os.getenv("HOST"),
    'port': os.getenv("PORT"),
    'dbname': os.getenv("DBNAME"),
    'user': os.getenv("USER"),
    'password': os.getenv("PASSWORD"),
}

def connect_to_db():
    """Establish a connection to the PostgreSQL database and return the connection object."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        print("Database connection failed:", e)
        return None