import psycopg2
import os
import sys

import psycopg2

load_dotenv()
DB_CONFIG = {
    'host': os.getenv("DB_HOST"),
    'port': os.getenv("DB_PORT"),
    'dbname': os.getenv("DB_NAME"),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
}

def upload_image(file_path):
    """Reads an image file and uploads it to a PostgreSQL database."""
    try:
        # Read the image file as binary
        with open(file_path, "rb") as file:
            binary_data = file.read()
        
        #  Connect to PostgreSQL
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        print("Connected to PostgreSQL database.")

        imageDescription = ("So it seems like the image description will"
                            "just continue regardless of the description length.")


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
file_location = r"C:\Users\cmcka\Downloads\tempMiscellaneousFolder\elisTest.JPG"  # Replace with actual file path
upload_image(file_location)
