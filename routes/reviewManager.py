import base64
from flask import Blueprint, request, render_template, redirect, url_for, session, jsonify
from databaseModule import connect_to_db

reviewManagerBP = Blueprint('reviewManager', __name__)

@reviewManagerBP.route('/reviewManager/public')
def reviewManagerPublic():
    if not session.get('loggedIn'):
        return redirect(url_for('employee.employeeLogin'))

    reviews_per_page = 5
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * reviews_per_page

    try:
        connect = connect_to_db()
        cursor = connect.cursor()
        cursor.execute('SELECT "NAME", "DESCRIPTION", "EMAIL", "DATE", "PUBLIC", "PRIMARY_KEY" FROM "REVIEWS" WHERE "PUBLIC" = TRUE ORDER BY "DATE" DESC LIMIT %s OFFSET %s' % (reviews_per_page, offset))
        reviewData = cursor.fetchall()

        public_reviews = [
            f"""
            <strong>Date:</strong> {row[3]}<br><br>
            <strong>Name:</strong> {row[0]}<br>
            <strong>Description:</strong> {row[1]}<br>
            <strong>Email:</strong> {row[2]}<br>
            <strong>Publicly displayed:</strong> {row[4]}
            <form action="/togglePublic/{row[5]}" method="POST">
                <button type="submit">Set to Private</button>
            </form>
            """ for row in reviewData
        ]

        # Get the total number of reviews to calculate pagination
        cursor.execute('SELECT COUNT(*) FROM "REVIEWS" WHERE "PUBLIC" = TRUE')
        total_reviews = cursor.fetchone()[0]

        # Calculate the total number of pages
        total_pages = (total_reviews + reviews_per_page - 1) // reviews_per_page

        # Generate pagination links
        pagination_links = ""
        for p in range(1, total_pages + 1):
            if p == page:
                pagination_links += f"<strong>{p}</strong> "
            else:
                pagination_links += f'<a href="/reviewManager/public?page={p}">{p}</a> '

        return render_template('reviewManagerPublic.html', formatted_reviews_public="<br><br>".join(public_reviews), pagination_links=pagination_links)

    except Exception as e:
        return jsonify({'Error': str(e)})

    finally:
        cursor.close()
        connect.close()


@reviewManagerBP.route('/reviewManager/private')
def reviewManagerPrivate():
    if not session.get('loggedIn'):
        return redirect(url_for('employee.employeeLogin'))

    reviews_per_page = 5
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * reviews_per_page

    try:
        connect = connect_to_db()
        cursor = connect.cursor()
        cursor.execute('SELECT "NAME", "DESCRIPTION", "EMAIL", "DATE", "PUBLIC", "PRIMARY_KEY" FROM "REVIEWS" WHERE "PUBLIC" = FALSE ORDER BY "DATE" DESC LIMIT %s OFFSET %s' % (reviews_per_page, offset))
        reviewData = cursor.fetchall()

        private_reviews = [
            f"""
            <strong>Date:</strong> {row[3]}<br><br>
            <strong>Name:</strong> {row[0]}<br>
            <strong>Description:</strong> {row[1]}<br>
            <strong>Email:</strong> {row[2]}<br>
            <strong>Publicly displayed:</strong> {row[4]}
            <form action="/togglePublic/{row[5]}" method="POST">
                <button type="submit">Set to Public</button>
            </form>
            """ for row in reviewData
        ]

        # Get the total number of reviews to calculate pagination
        cursor.execute('SELECT COUNT(*) FROM "REVIEWS" WHERE "PUBLIC" = FALSE')
        total_reviews = cursor.fetchone()[0]
        total_pages = (total_reviews + reviews_per_page - 1) // reviews_per_page
        pagination_links = ""
        for p in range(1, total_pages + 1):
            if p == page:
                pagination_links += f"<strong>{p}</strong> "
            else:
                pagination_links += f'<a href="/reviewManager/private?page={p}">{p}</a> '

        return render_template('reviewManagerPrivate.html', formatted_reviews_private="<br><br>".join(private_reviews), pagination_links=pagination_links)

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

    # Identify which table to modify (default is REVIEWS)
    table = request.form.get('table', 'REVIEWS')

    cursor.execute(f'SELECT "PUBLIC" FROM "{table}" WHERE "PRIMARY_KEY" = %s', (key,))
    currentStatus = cursor.fetchone()[0]
    newStatus = not currentStatus

    cursor.execute(f'UPDATE "{table}" SET "PUBLIC" = %s WHERE "PRIMARY_KEY" = %s', (newStatus, key))
    connect.commit()
    if table == 'REVIEWS':
        if newStatus == True:
            return redirect(url_for('reviewManager.reviewManagerPublic' if table == 'REVIEWS' else 'employee.galleryManager'))
        else:
            return redirect(url_for('reviewManager.reviewManagerPrivate'))
    else:
        return redirect(url_for('galleryManager.galleryManager'))