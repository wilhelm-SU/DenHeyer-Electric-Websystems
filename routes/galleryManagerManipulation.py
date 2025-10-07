import io
from flask import Blueprint, request, render_template, redirect, url_for, session, jsonify
from databaseModule import connect_to_db
from PIL import Image

galleryManagerManipulationBP = Blueprint('galleryManagerManipulation', __name__)

@galleryManagerManipulationBP.route('/deleteImage/<int:primary_key>', methods=['POST'])
def deleteImage(primary_key):
    if not session.get('loggedIn'):
        return redirect(url_for('employee.employeeLogin'))

    try:
        connect = connect_to_db()
        cursor = connect.cursor()

        # Deleting from GALLERY_META automatically removes related images in GALLERY_IMAGE
        cursor.execute('DELETE FROM "GALLERY_META" WHERE "PRIMARY_KEY" = %s', (primary_key,))
        connect.commit()
        print(f"Deleted image with PRIMARY_KEY = {primary_key}")

    except Exception as e:
        print(f"Error deleting image: {e}")

    finally:
        if cursor:
            cursor.close()
        if connect:
            connect.close()

    return redirect(url_for('galleryManager.galleryManager'))

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

#so this is going to be the spot where the image gets split into high/low resolution

    try:
        # Step 1: Load the original image
        image = Image.open(image_file)

        # Save full-res image bytes
        full_res_bytes = io.BytesIO()
        image.save(full_res_bytes, format='JPEG')
        full_res_bytes = full_res_bytes.getvalue()

        # Create thumbnail (lazy-load version)
        thumbnail_size = (300, 300)  # adjust as needed for display speed/quality
        image.thumbnail(thumbnail_size)     #this might need to be adjusted for mobile view

        thumbnail_bytes = io.BytesIO()
        image.save(thumbnail_bytes, format='JPEG')
        thumbnail_bytes = thumbnail_bytes.getvalue()

        # Insert into DB
        connect = connect_to_db()
        cursor = connect.cursor()

        # Insert metadata first
        cursor.execute('''
                INSERT INTO "GALLERY_META" ("DESCRIPTION", "PUBLIC")
                VALUES (%s, %s)
                RETURNING "PRIMARY_KEY"
            ''', (description, public))
        gallery_key = cursor.fetchone()[0]

        # Insert image data linked to metadata
        cursor.execute('''
                INSERT INTO "GALLERY_IMAGE" ("GALLERY_KEY", "THUMBNAIL", "FULL_RES")
                VALUES (%s, %s, %s)
            ''', (gallery_key, thumbnail_bytes, full_res_bytes))

        connect.commit()
        print(f"Inserted image with GALLERY_KEY = {gallery_key}")

    except Exception as e:
        print(f"Error inserting image: {e}")
        return "Error inserting image", 500

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

# New toggle function for public/private
#
@galleryManagerManipulationBP.route('/togglePublic/<int:primary_key>', methods=['POST'])
def togglePublic(primary_key):
    if not session.get('loggedIn'):
        return redirect(url_for('employee.employeeLogin'))

    try:
        connect = connect_to_db()
        cursor = connect.cursor()

        # Toggle PUBLIC value in GALLERY_META
        cursor.execute('''
            UPDATE "GALLERY_META"
            SET "PUBLIC" = NOT "PUBLIC"
            WHERE "PRIMARY_KEY" = %s
        ''', (primary_key,))

        connect.commit()
        print(f"Toggled PUBLIC for image PRIMARY_KEY={primary_key}")

    except Exception as e:
        print(f"Error toggling public: {e}")

    finally:
        if cursor:
            cursor.close()
        if connect:
            connect.close()

    return redirect(url_for('galleryManager.galleryManager'))



