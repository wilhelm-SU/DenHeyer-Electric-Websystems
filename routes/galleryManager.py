import base64
from flask import render_template, jsonify, Blueprint, request, redirect, url_for, session
from databaseModule import connect_to_db


galleryManagerBP = Blueprint('galleryManager', __name__)


#route for gallery manager
@galleryManagerBP.route('/galleryManager', methods=['GET', 'POST'])
def galleryManager():
    if not session.get('loggedIn'):  # extremely important as this prevents non authorized users from accessing pages by simply writing in url
        return redirect(url_for('employee.employeeLogin'))

    try:
        connect = connect_to_db()
        cursor = connect.cursor()
        cursor.execute('SELECT "PRIMARY_KEY", "IMAGE_DATA", "DESCRIPTION", "PUBLIC" FROM "GALLERY" ORDER BY "PRIMARY_KEY" ASC')
        print("Query executed successfully")

        imageData = cursor.fetchall()

        image_list = []
        for data in imageData:
            if data[1]:
                base64_imageData = base64.b64encode(data[1]).decode('utf-8')
                image_list.append((data[0], base64_imageData, data[2], data[3]))

        if not image_list:
            return '''No images available.<br>'''

        formatted_gallery = "<br><br>".join(
            [f"""
            <strong>Image:</strong><br>
            <img src="data:image/jpeg;base64,{row[1]}" alt="Gallery Image" style="max-width: 300px; max-height: 300px;"><br><br>
            <strong>Description:</strong>{row[2]}<br><br>
            <strong>Publicly displayed:</strong>{row[3]}<br><br>
            <form action="/togglePublic/{row[0]}" method="POST">
                <input type="hidden" name="table" value="GALLERY">
                <button type="submit">
                    {'Set to Private' if row[3] else 'Set to Public'}
                </button>
            </form>

            <form action="/deleteImage/{row[0]}" method="POST" style="display:inline; margin-left: 10px;">
                <input type="hidden" name="table" value="GALLERY">
                <button type="submit" onclick="return confirm('Are you sure you want to delete this image?');">
                    Delete
                </button>
            </form>

            """ for row in image_list])

        #funtion to delete an image from the gallery in the database


        return f'''<h2>Welcome to the gallery manager</h2>
                    Here you can accept or reject images from being displayed
                    in the public gallery.<br><br>
                    <a href="/insertImagePage">Add New Image</a>
                    {formatted_gallery}
                    <br><br>
                    <a href="/employeePortal">Return</a>''', 200
        #/galleryManagerManipulation/insertImagePage

        print(imageData)
        print('why is there an error bellow?')

    finally:
        try:
            if cursor:
                cursor.close()
            if connect:
                connect.close()
        except Exception as e:
            # Optionally log any errors related to closing
            print(f"Error closing connection: {e}")



