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

        cursor.execute("""
            SELECT
                gp."PROJECT_ID",
                gp."TITLE",
                gp."DESCRIPTION",
                gi."THUMBNAIL"
            FROM "GALLERY_PROJECT" gp
            LEFT JOIN "GALLERY_IMAGE" gi
                ON gi."IMAGE_ID" = (
                    SELECT "IMAGE_ID"
                    FROM "GALLERY_IMAGE"
                    WHERE "PROJECT_ID" = gp."PROJECT_ID"
                    ORDER BY "IMAGE_ID"
                    LIMIT 1
                )
            WHERE gp."PUBLIC" = TRUE
            ORDER BY gp."CREATED_AT" DESC;
        """)

        projects = []

        for row in cursor.fetchall():
            thumbnail = None

            if row[3]:
                thumbnail = base64.b64encode(row[3]).decode("utf-8")

            projects.append({
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "thumbnail": thumbnail
            })

    except Exception as e:
        return jsonify({"Error": str(e)})

    finally:
        if cursor:
            cursor.close()
        if connect:
            connect.close()

    return render_template(
        "gallery.html",
        projects=projects
    )

@galleryBP.route('/gallery/project/<int:project_id>')
def project_gallery(project_id):
    try:
        connect = connect_to_db()
        cursor = connect.cursor()

        cursor.execute("""
            SELECT
                gp."TITLE",
                gp."DESCRIPTION"
            FROM "GALLERY_PROJECT" gp
            WHERE gp."PROJECT_ID"=%s;
        """, (project_id,))

        project = cursor.fetchone()

        if not project:
            return "Project not found", 404

        cursor.execute("""
            SELECT
                "IMAGE_ID",
                "THUMBNAIL"
            FROM "GALLERY_IMAGE"
            WHERE "PROJECT_ID"=%s
            ORDER BY "IMAGE_ID";
        """, (project_id,))

        images = []

        for row in cursor.fetchall():
            images.append({
                "id": row[0],
                "thumbnail": base64.b64encode(row[1]).decode("utf-8")
            })

    except Exception as e:
        return jsonify({"Error": str(e)})

    finally:
        if cursor:
            cursor.close()
        if connect:
            connect.close()

    return render_template(
        "projectGallery.html",
        project={
            "id": project_id,
            "title": project[0],
            "description": project[1]
        },
        image_list=images
    )

@galleryBP.route('/get_fullres/<int:image_id>')
def get_fullres(image_id):
    try:
        connect = connect_to_db()
        cursor = connect.cursor()

        cursor.execute("""
            SELECT "FULL_RES"
            FROM "GALLERY_IMAGE"
            WHERE "IMAGE_ID"=%s;
        """, (image_id,))

        result = cursor.fetchone()

        if result and result[0]:
            return send_file(
                BytesIO(result[0]),
                mimetype="image/jpeg"
            )

        return "Image not found", 404

    except Exception as e:
        return jsonify({"Error": str(e)})

    finally:
        if cursor:
            cursor.close()
        if connect:
            connect.close()