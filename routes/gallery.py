import base64
from flask import Blueprint, render_template, jsonify
from databaseModule import connect_to_db

galleryBP = Blueprint('gallery', __name__)

@galleryBP.route('/gallery')
def gallery():
    try:
        connect = connect_to_db()
        cursor = connect.cursor()
        cursor.execute('SELECT "PRIMARY_KEY", "IMAGE_DATA", "DESCRIPTION" FROM "GALLERY"')
        print("Query executed successfully")
        imageData = cursor.fetchall()
        print("Image Data:", imageData)  # Check the fetched raw data

        image_list = []
        for data in imageData:
            if data[1]:
                base64_imageData = base64.b64encode(data[1]).decode('utf-8')
                image_list.append((data[0], base64_imageData, data[2]))

        # Debug: Check if image_list is populated
        #print("Image List:", image_list)  # Ensure image_list is populated

    except Exception as e:
        return jsonify({'Error': str(e)})

    # Debug: Check that image_list is passed to the template
    #print("Passing image_list to HTML Template:", image_list)

    return render_template('gallery.html', image_list=image_list)
