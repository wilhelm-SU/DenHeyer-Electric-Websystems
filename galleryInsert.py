import psycopg2
import os
import sys

'''
host = 'dpg-curuecjv2p9s73aprlvg-a.oregon-postgres.render.com'  # Example: 'localhost' or an IP address
port = '5432'  # Example: '5432'
dbname = 'denheyer_webserver'  # Your database name
user = 'denheyer_webserver_user'  # Your database username
password = 'CEu8cjkwWRcBDCjjZu0GhUBwhHA2Jush'  # Your database password
'''

import psycopg2

#  PostgreSQL Connection Details
DB_NAME = 'denheyer_webserver'
DB_USER = 'denheyer_webserver_user'
DB_PASSWORD = 'CEu8cjkwWRcBDCjjZu0GhUBwhHA2Jush'  
DB_HOST = 'dpg-curuecjv2p9s73aprlvg-a.oregon-postgres.render.com'  # e.g., "localhost" or Render database URL
DB_PORT = '5432'  # Default is "5432"

def upload_image(file_path):
    """Reads an image file and uploads it to a PostgreSQL database."""
    try:
        # Read the image file as binary
        with open(file_path, "rb") as file:
            binary_data = file.read()
        
        #  Connect to PostgreSQL
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cur = conn.cursor()
        
        print("Connected to PostgreSQL database.")

        imageDescription = "This is a test image."


        #   Insert the image data into the table
        filename = file_path.split("/")[-1]  # Extract filename from path
        cur.execute('INSERT INTO "GALLERY" ("IMAGE_DATA", "DESCRIPTION") VALUES (%s, %s)', (binary_data, imageDescription))
        
        #   Commit and close connection
        conn.commit()
        cur.close()
        conn.close()

        print(f"Successfully uploaded '{filename}' to PostgreSQL.")

    except Exception as e:
        print(f"Error: {e}")

#   Example Usage

#C:\Users\cmcka\Downloads\tempMiscellaneousFolder\image.jpg
file_location = r"C:\Users\cmcka\Downloads\tempMiscellaneousFolder\FlowerWater.jpg"  # Replace with actual file path
upload_image(file_location)

