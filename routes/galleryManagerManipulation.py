from flask import Blueprint, request, render_template, redirect, url_for, session, jsonify
from databaseModule import connect_to_db

galleryManagerManipulationBP = Blueprint('galleryManagerManipulation', __name__)

@galleryManagerManipulationBP.route('/deleteImage/<int:primary_key>', methods=['POST'])
def deleteImage(primary_key):
    if not session.get('loggedIn'):
        return redirect(url_for('employee.employeeLogin'))

    try:
        connect = connect_to_db()
        cursor = connect.cursor()
        cursor.execute('DELETE FROM "GALLERY" WHERE "PRIMARY_KEY" = %s', (primary_key,))
        connect.commit()
        print(f"Deleted image with PRIMARY_KEY = {primary_key}")
    except Exception as e:
        print(f"Error deleting image: {e}")
    finally:
        if cursor:
            cursor.close()
        if connect:
            connect.close()

    return redirect(url_for('galleryManager.galleryManager'))  # Redirect to gallery manager after deletion

@galleryManagerManipulationBP.route('/insertImage', methods=['POST'])
def insertImage():
    if not session.get('loggedIn'):
        return redirect(url_for('employee.employeeLogin'))

    # Get image data from the form
    description = request.form.get('description')
    public = request.form.get('public') == 'on'  # Checkbox logic
    image_file = request.files.get('image')

    if not image_file:
        return "No image uploaded", 400

    image_bytes = image_file.read()

    try:
        connect = connect_to_db()
        cursor = connect.cursor()

        cursor.execute('''
            INSERT INTO "GALLERY" ("IMAGE_DATA", "DESCRIPTION", "PUBLIC")
            VALUES (%s, %s, %s)
        ''', (image_bytes, description, public))

        connect.commit()
        print("Image inserted successfully")
    except Exception as e:
        print(f"Error inserting image: {e}")
    finally:
        if cursor:
            cursor.close()
        if connect:
            connect.close()

    return redirect(url_for('galleryManager.galleryManager'))

@galleryManagerManipulationBP.route('/insertImagePage', methods=['GET'])
def insertImagePage():
    if not session.get('loggedIn'):
        return redirect(url_for('employee.employeeLogin'))

    return render_template('uploadImage.html')


