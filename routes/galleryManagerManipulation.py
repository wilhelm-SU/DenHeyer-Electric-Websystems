import io
from flask import Blueprint, request, render_template, redirect, url_for, session, jsonify
from databaseModule import connect_to_db
from PIL import Image

galleryManagerManipulationBP = Blueprint('galleryManagerManipulation', __name__)

@galleryManagerManipulationBP.route('/deleteImage/<int:image_id>', methods=['POST'])
def deleteImage(image_id):
    if not session.get('loggedIn'):
        return redirect(url_for('employee.employeeLogin'))

    connect = None
    cursor = None

    try:
        connect = connect_to_db()
        cursor = connect.cursor()

        # Find the project this image belongs to
        cursor.execute("""
            SELECT "PROJECT_ID"
            FROM "GALLERY_IMAGE"
            WHERE "IMAGE_ID" = %s
        """, (image_id,))

        result = cursor.fetchone()

        if not result:
            return "Image not found.", 404

        project_id = result[0]

        # Delete the image
        cursor.execute("""
            DELETE FROM "GALLERY_IMAGE"
            WHERE "IMAGE_ID" = %s
        """, (image_id,))

        connect.commit()

    except Exception as e:
        if connect:
            connect.rollback()
        print(e)
        return "Error deleting image.", 500

    finally:
        if cursor:
            cursor.close()
        if connect:
            connect.close()

    return redirect(
        url_for(
            'galleryManager.projectManager',
            project_id=project_id
        )
    )
@galleryManagerManipulationBP.route('/createProjectPage', methods=['GET'])
def createProjectPage():
    if not session.get('loggedIn'):
        return redirect(url_for('employee.employeeLogin'))

    return render_template('createProject.html')

@galleryManagerManipulationBP.route('/createProject', methods=['POST'])
def createProject():
    if not session.get('loggedIn'):
        return redirect(url_for('employee.employeeLogin'))

    title = request.form.get("title")
    description = request.form.get("description")
    public = request.form.get("public") == "on"

    connect = connect_to_db()
    cursor = connect.cursor()

    cursor.execute("""
    INSERT INTO "GALLERY_PROJECT"
    ("TITLE","DESCRIPTION","PUBLIC")
    VALUES (%s,%s,%s)
    RETURNING "PROJECT_ID"
    """, (title, description, public))

    project_id = cursor.fetchone()[0]

    connect.commit()

    cursor.close()
    connect.close()

    return redirect(
        url_for(
            "galleryManager.projectManager",
            project_id=project_id
        )
    )
@galleryManagerManipulationBP.route('/insertImage', methods=['POST'])
def insertImage():

    if not session.get('loggedIn'):
        return redirect(url_for('employee.employeeLogin'))

    project_id = request.form.get("project_id", type=int)

    files = request.files.getlist("image")

    if not files:
        return "No images uploaded", 400

    connect = None
    cursor = None

    try:
        connect = connect_to_db()
        cursor = connect.cursor()

        for image_file in files:

            image = Image.open(image_file)

            if image.mode != "RGB":
                image = image.convert("RGB")

            full_buffer = io.BytesIO()
            image.save(full_buffer, format="JPEG", quality=95)

            thumb = image.copy()
            thumb.thumbnail((300, 300))

            thumb_buffer = io.BytesIO()
            thumb.save(thumb_buffer, format="JPEG", quality=85)

            cursor.execute("""
                INSERT INTO "GALLERY_IMAGE"
                ("PROJECT_ID","THUMBNAIL","FULL_RES")
                VALUES (%s,%s,%s)
            """, (
                project_id,
                thumb_buffer.getvalue(),
                full_buffer.getvalue()
            ))

        connect.commit()

    except Exception as e:
        if connect:
            connect.rollback()
        print(e)
        return "Error uploading images.", 500

    finally:
        if cursor:
            cursor.close()
        if connect:
            connect.close()

    return redirect(
        url_for(
            "galleryManager.projectManager",
            project_id=project_id
        )
    )

# New toggle function for public/private
#
@galleryManagerManipulationBP.route('/togglePublic/<int:project_id>', methods=['POST'])
def togglePublic(project_id):
    if not session.get('loggedIn'):
        return redirect(url_for('employee.employeeLogin'))

    connect = connect_to_db()
    cursor = connect.cursor()

    cursor.execute("""
        UPDATE "GALLERY_PROJECT"
        SET "PUBLIC" = NOT "PUBLIC"
        WHERE "PROJECT_ID"=%s
    """,(project_id,))

    connect.commit()

    cursor.close()
    connect.close()

    return redirect(url_for('galleryManager.galleryManager'))

@galleryManagerManipulationBP.route('/deleteProject/<int:project_id>', methods=['POST'])
def deleteProject(project_id):
    if not session.get('loggedIn'):
        return redirect(url_for('employee.employeeLogin'))

    connect = connect_to_db()
    cursor = connect.cursor()

    cursor.execute("""
        DELETE FROM "GALLERY_PROJECT"
        WHERE "PROJECT_ID"=%s
    """,(project_id,))

    connect.commit()

    cursor.close()
    connect.close()

    return redirect(url_for('galleryManager.galleryManager'))

@galleryManagerManipulationBP.route('/insertImagePage')
def insertImagePage():

    if not session.get('loggedIn'):
        return redirect(url_for('employee.employeeLogin'))

    connect = connect_to_db()
    cursor = connect.cursor()

    cursor.execute("""
        SELECT
            "PROJECT_ID",
            "TITLE"
        FROM "GALLERY_PROJECT"
        ORDER BY "TITLE";
    """)

    project_list = [
        {
            "id": row[0],
            "title": row[1]
        }
        for row in cursor.fetchall()
    ]

    cursor.close()
    connect.close()

    return render_template(
        "uploadImage.html",
        project_list=project_list
    )


