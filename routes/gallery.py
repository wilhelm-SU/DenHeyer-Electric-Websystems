import base64
from flask import Blueprint, render_template, jsonify, send_file
from io import BytesIO
from databaseModule import connect_to_db

galleryBP = Blueprint('gallery', __name__)

@galleryBP.route('/gallery')
def gallery():
    try:
        connect = connect_to_db()
        cursor = connect.cursor()
        cursor.execute('''
            SELECT gm."PRIMARY_KEY", gi."THUMBNAIL", gm."DESCRIPTION"
            FROM "GALLERY_META" gm
            JOIN "GALLERY_IMAGE" gi
            ON gm."PRIMARY_KEY" = gi."GALLERY_KEY"
            WHERE gm."PUBLIC" = TRUE
            ORDER BY gm."PRIMARY_KEY" ASC;
        ''')

        imageData = cursor.fetchall()

        image_list = []
        for data in imageData:
            if data[1]:
                base64_thumb = base64.b64encode(data[1]).decode('utf-8')
                image_list.append({
                    'id': data[0],
                    'thumbnail': base64_thumb,
                    'description': data[2]
                })

    except Exception as e:
        return jsonify({'Error': str(e)})

    finally:
        if cursor:
            cursor.close()
        if connect:
            connect.close()

    return render_template('gallery.html', image_list=image_list)


@galleryBP.route('/get_fullres/<int:image_id>')
def get_fullres(image_id):
    """Serve full-resolution image on-demand for lazy loading."""
    try:
        connect = connect_to_db()
        cursor = connect.cursor()
        cursor.execute('''
            SELECT "FULL_RES" FROM "GALLERY_IMAGE"
            WHERE "GALLERY_KEY" = %s;
        ''', (image_id,))
        result = cursor.fetchone()

        if result and result[0]:
            return send_file(BytesIO(result[0]), mimetype='image/jpeg')
        else:
            return "Image not found", 404

    except Exception as e:
        return jsonify({'Error': str(e)})

    finally:
        if cursor:
            cursor.close()
        if connect:
            connect.close()
