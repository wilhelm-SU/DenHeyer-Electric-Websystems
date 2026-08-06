import base64
from flask import render_template, Blueprint, redirect, url_for, session
from databaseModule import connect_to_db

galleryManagerBP = Blueprint(
    'galleryManager',
    __name__,
    url_prefix='/galleryManager'
)


@galleryManagerBP.route('/galleryManager', methods=['GET'])
def galleryManager():

    if not session.get('loggedIn'):
        return redirect(url_for('employee.employeeLogin'))

    try:
        connect = connect_to_db()
        cursor = connect.cursor()

        cursor.execute("""
            SELECT
                gp."PROJECT_ID",
                gp."TITLE",
                gp."DESCRIPTION",
                gp."PUBLIC",
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

            ORDER BY gp."CREATED_AT" DESC;
        """)

        project_list = []

        for row in cursor.fetchall():

            thumbnail = None

            if row[4]:
                thumbnail = base64.b64encode(row[4]).decode("utf-8")

            project_list.append({
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "public": row[3],
                "thumbnail": thumbnail
            })

        return render_template(
            "galleryManager.html",
            project_list=project_list
        )

    except Exception as e:
        return f"Database Error: {e}"

    finally:
        if cursor:
            cursor.close()

        if connect:
            connect.close()

@galleryManagerBP.route('/project/<int:project_id>')
def projectManager(project_id):

    if not session.get('loggedIn'):
        return redirect(url_for('employee.employeeLogin'))

    connect = None
    cursor = None

    try:
        connect = connect_to_db()
        cursor = connect.cursor()

        # Get project info
        cursor.execute("""
            SELECT
                "TITLE",
                "DESCRIPTION",
                "PUBLIC"
            FROM "GALLERY_PROJECT"
            WHERE "PROJECT_ID"=%s
        """, (project_id,))

        project = cursor.fetchone()

        if not project:
            return "Project not found", 404

        # Get all images in project
        cursor.execute("""
            SELECT
                "IMAGE_ID",
                "THUMBNAIL"
            FROM "GALLERY_IMAGE"
            WHERE "PROJECT_ID"=%s
            ORDER BY "IMAGE_ID"
        """, (project_id,))

        image_list = []

        for row in cursor.fetchall():

            image_list.append({
                "id": row[0],
                "thumbnail": base64.b64encode(row[1]).decode("utf-8")
            })

    finally:

        if cursor:
            cursor.close()

        if connect:
            connect.close()

    return render_template(
        "projectImages.html",
        project={
            "id": project_id,
            "title": project[0],
            "description": project[1],
            "public": project[2]
        },
        image_list=image_list
    )