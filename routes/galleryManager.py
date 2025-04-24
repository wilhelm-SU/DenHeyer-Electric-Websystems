import base64
from flask import render_template, jsonify, Blueprint, request, redirect, url_for, session
from databaseModule import connect_to_db


galleryManagerBP = Blueprint('galleryManager', __name__)


#route for gallery manager
@galleryManagerBP.route('/galleryManager', methods=['GET', 'POST'])
def galleryManager():
    if not session.get('loggedIn'):
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
        #The grid display for the images in the gallery, inspired momstly from gallery.py
        formatted_gallery = '''
        <style>
            .gallery-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 20px;
                padding: 20px;
            }
            .image-card {
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 10px;
                box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
                text-align: center;
                background-color: #f9f9f9;
            }
            .image-card img {
                max-width: 100%;
                height: auto;
                border-radius: 4px;
            }
        </style>

        <div class="gallery-grid">
        ''' + "\n".join([
            f"""
            <div class="image-card">
                <img src="data:image/jpeg;base64,{row[1]}" alt="Gallery Image"><br><br>
                <strong>Description:</strong> {row[2]}<br><br>
                <strong>Publicly displayed:</strong> {row[3]}<br><br>
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
            </div>
            """ for row in image_list
        ]) + '</div>'

        return f'''
            <h2>Welcome to the gallery manager</h2>
            Here you can accept or reject images from being displayed
            in the public gallery.<br><br>
            <a href="/insertImagePage">Add New Image</a>
            {formatted_gallery}
            <br><br>
            <a href="/employeePortal">Return</a>
        ''', 200

    finally:
        try:
            if cursor:
                cursor.close()
            if connect:
                connect.close()
        except Exception as e:
            print(f"Error closing connection: {e}")



