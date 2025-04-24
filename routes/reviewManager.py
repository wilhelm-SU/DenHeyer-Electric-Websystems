import base64
from flask import Blueprint, request, render_template, redirect, url_for, session, jsonify
from databaseModule import connect_to_db

reviewManagerBP = Blueprint('reviewManager', __name__)

@reviewManagerBP.route('/reviewManager/public')
def reviewManagerPublic():
    if not session.get('loggedIn'):
        return redirect(url_for('employee.employeeLogin'))

    try:
        connect = connect_to_db()
        cursor = connect.cursor()
        cursor.execute('SELECT "NAME", "DESCRIPTION", "EMAIL", "DATE", "PUBLIC", "PRIMARY_KEY" FROM "REVIEWS"')
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
            """ for row in reviewData if row[4]
        ]

        return render_template('reviewManagerPublic.html', formatted_reviews_public="<br><br>".join(public_reviews))

    except Exception as e:
        return jsonify({'Error': str(e)})

    finally:
        cursor.close()
        connect.close()


@reviewManagerBP.route('/reviewManager/private')
def reviewManagerPrivate():
    if not session.get('loggedIn'):
        return redirect(url_for('employee.employeeLogin'))

    try:
        connect = connect_to_db()
        cursor = connect.cursor()
        cursor.execute('SELECT "NAME", "DESCRIPTION", "EMAIL", "DATE", "PUBLIC", "PRIMARY_KEY" FROM "REVIEWS"')
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
            """ for row in reviewData if not row[4]
        ]

        return render_template('reviewManagerPrivate.html', formatted_reviews_private="<br><br>".join(private_reviews))

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

    return redirect(url_for('employee.reviewManager' if table == 'REVIEWS' else 'employee.galleryManager'))
