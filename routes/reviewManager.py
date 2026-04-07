import base64
from flask import Blueprint, request, render_template, redirect, url_for, session, jsonify
from databaseModule import connect_to_db

reviewManagerBP = Blueprint('reviewManager', __name__, url_prefix='/reviewManager')


@reviewManagerBP.route('/public')
def reviewManagerPublic():
    if not session.get('loggedIn'):
        return redirect(url_for('employee.employeeLogin'))

    reviews_per_page = 5
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * reviews_per_page

    try:
        connect = connect_to_db()
        cursor = connect.cursor()
        cursor.execute(
            '''
            SELECT "NAME", "DESCRIPTION", "EMAIL", "DATE", "PUBLIC", "PRIMARY_KEY"
            FROM "REVIEWS"
            WHERE "PUBLIC" = TRUE
            ORDER BY "DATE" DESC
            LIMIT %s OFFSET %s
            ''',
            (reviews_per_page, offset)
        )
        reviewData = cursor.fetchall()

        public_reviews = []
        for row in reviewData:
            toggle_url = url_for('reviewManager.togglePublic', key=row[5])
            delete_url = url_for('reviewManager.deleteReview')
            public_reviews.append(f"""
                <strong>Date:</strong> {row[3]}<br><br>
                <strong>Name:</strong> {row[0]}<br>
                <strong>Description:</strong> {row[1]}<br>
                <strong>Email:</strong> {row[2]}<br>
                <strong>Publicly displayed:</strong> {row[4]}
                <form action="{toggle_url}" method="POST">
                    <button type="submit">Set to Private</button>
                </form>
                <form action="{delete_url}" method="POST" style="display:inline;">
                    <input type="hidden" name="request_id" value="{row[5]}">
                    <button type="submit">Delete</button>
                </form>
            """)

        # Pagination
        cursor.execute('SELECT COUNT(*) FROM "REVIEWS" WHERE "PUBLIC" = TRUE')
        total_reviews = cursor.fetchone()[0]
        total_pages = (total_reviews + reviews_per_page - 1) // reviews_per_page

        pagination_links = ""
        for p in range(1, total_pages + 1):
            if p == page:
                pagination_links += f"<strong>{p}</strong> "
            else:
                pagination_links += f'<a href="{url_for("reviewManager.reviewManagerPublic")}?page={p}">{p}</a> '

        return render_template(
            'reviewManagerPublic.html',
            formatted_reviews_public="<br><br>".join(public_reviews),
            pagination_links=pagination_links
        )

    except Exception as e:
        return jsonify({'Error': str(e)})
    finally:
        cursor.close()
        connect.close()


@reviewManagerBP.route('/private')
def reviewManagerPrivate():
    if not session.get('loggedIn'):
        return redirect(url_for('employee.employeeLogin'))

    reviews_per_page = 5
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * reviews_per_page

    try:
        connect = connect_to_db()
        cursor = connect.cursor()
        cursor.execute(
            '''
            SELECT "NAME", "DESCRIPTION", "EMAIL", "DATE", "PUBLIC", "PRIMARY_KEY"
            FROM "REVIEWS"
            WHERE "PUBLIC" = FALSE
            ORDER BY "DATE" DESC
            LIMIT %s OFFSET %s
            ''',
            (reviews_per_page, offset)
        )
        reviewData = cursor.fetchall()

        private_reviews = []
        for row in reviewData:
            toggle_url = url_for('reviewManager.togglePublic', key=row[5])
            delete_url = url_for('reviewManager.deleteReview')
            private_reviews.append(f"""
                <strong>Date:</strong> {row[3]}<br><br>
                <strong>Name:</strong> {row[0]}<br>
                <strong>Description:</strong> {row[1]}<br>
                <strong>Email:</strong> {row[2]}<br>
                <strong>Publicly displayed:</strong> {row[4]}
                <form action="{toggle_url}" method="POST">
                    <button type="submit">Set to Public</button>
                </form>
                <form action="{delete_url}" method="POST" style="display:inline;">
                    <input type="hidden" name="request_id" value="{row[5]}">
                    <button type="submit">Delete</button>
                </form>
            """)

        # Pagination
        cursor.execute('SELECT COUNT(*) FROM "REVIEWS" WHERE "PUBLIC" = FALSE')
        total_reviews = cursor.fetchone()[0]
        total_pages = (total_reviews + reviews_per_page - 1) // reviews_per_page

        pagination_links = ""
        for p in range(1, total_pages + 1):
            if p == page:
                pagination_links += f"<strong>{p}</strong> "
            else:
                pagination_links += f'<a href="{url_for("reviewManager.reviewManagerPrivate")}?page={p}">{p}</a> '

        return render_template(
            'reviewManagerPrivate.html',
            formatted_reviews_private="<br><br>".join(private_reviews),
            pagination_links=pagination_links
        )

    except Exception as e:
        return jsonify({'Error': str(e)})
    finally:
        cursor.close()
        connect.close()


@reviewManagerBP.route('/togglePublic/<key>', methods=['POST'])
def togglePublic(key):
    if not session.get('loggedIn'):
        return redirect(url_for('employee.employeeLogin'))

    connect = connect_to_db()
    cursor = connect.cursor()

    try:
        cursor.execute('SELECT "PUBLIC" FROM "REVIEWS" WHERE "PRIMARY_KEY" = %s', (key,))
        result = cursor.fetchone()
        if not result:
            return jsonify({'Error': f'No review found with key {key}'}), 404

        currentStatus = bool(result[0])
        newStatus = not currentStatus

        cursor.execute('UPDATE "REVIEWS" SET "PUBLIC" = %s WHERE "PRIMARY_KEY" = %s', (newStatus, key))
        connect.commit()

        # Redirect based on new status
        if newStatus:
            return redirect(url_for('reviewManager.reviewManagerPublic'))
        else:
            return redirect(url_for('reviewManager.reviewManagerPrivate'))

    except Exception as e:
        return jsonify({'Error': str(e)})
    finally:
        cursor.close()
        connect.close()


@reviewManagerBP.route('/deleteReview/', methods=['POST'])
def deleteReview():
    if not session.get('loggedIn'):
        return redirect(url_for('employee.employeeLogin'))

    try:
        request_id = request.form.get('request_id')
        if not request_id:
            return jsonify({'Error': 'Missing "request_id" parameter'}), 400

        connect = connect_to_db()
        cursor = connect.cursor()
        cursor.execute('DELETE FROM "REVIEWS" WHERE "PRIMARY_KEY" = %s', (request_id,))
        connect.commit()

        if cursor.rowcount == 0:
            return jsonify({'Error': 'No review found with that ID'}), 404

        return redirect(url_for('reviewManager.reviewManagerPrivate'))

    except Exception as e:
        return jsonify({'Error': str(e)})
    finally:
        try:
            if cursor:
                cursor.close()
            if connect:
                connect.close()
        except Exception as e:
            print(f"Error closing connection: {e}")