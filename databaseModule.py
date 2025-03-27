import psycopg2

# Database credentials
DB_CONFIG = {
    'host': 'dpg-curuecjv2p9s73aprlvg-a.oregon-postgres.render.com',
    'port': '5432',
    'dbname': 'denheyer_webserver',
    'user': 'denheyer_webserver_user',
    'password': 'CEu8cjkwWRcBDCjjZu0GhUBwhHA2Jush'
}

def connect_to_db():
    """Establish a connection to the PostgreSQL database and return the connection object."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        print("Database connection failed:", e)
        return None