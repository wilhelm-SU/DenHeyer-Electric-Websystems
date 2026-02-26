from dotenv import load_dotenv
import psycopg2, os

# Database credentials
load_dotenv()
DB_CONFIG = {
    'host': os.getenv("DB_HOST"),
    'port': os.getenv("DB_PORT"),
    'dbname': os.getenv("DB_NAME"),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
}

def connect_to_db():
    """Establish a connection to the PostgreSQL database and return the connection object."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        print("Database connection failed:", e)
        return None

