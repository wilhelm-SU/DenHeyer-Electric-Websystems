import base64
from flask import Blueprint, request, render_template, redirect, url_for, session, jsonify
from databaseModule import connect_to_db

reviewManagerBP = Blueprint('reviewManager', __name__)

@reviewManagerBP.route('/reviewManager', methods=['GET', 'POST'])
def reviewManager():
    if not session.get('loggedIn'): #extremely important as this prevents non authorized users from accessing pages by simply writing in url
        return redirect(url_for('employee.employeeLogin'))

    try:
        connect = connect_to_db()
        cursor = connect.cursor()
        cursor.execute('SELECT "NAME", "DESCRIPTION", "EMAIL", "DATE", "PUBLIC", "PRIMARY_KEY" FROM "REVIEWS"')

        print("Query executed successfully")

        reviewData = cursor.fetchall()

        if not reviewData:
            return '''No reviews available.<br>'''

        # Format reviews as templates
        formatted_reviews = "<br><br>".join(
            [f"""
            <strong>Date:</strong> {row[3]}<br><br>
            <strong>Name:</strong> {row[0]}<br>
            <strong>Description:</strong> {row[1]}<br>
            <strong>Email:</strong> {row[2]}<br>
            <strong>Publicly displayed:</strong> {row[4]}
            <form action="/togglePublic/{row[5]}" method="POST">
                <button type="submit">
                    {'Set to Private' if row[4] else 'Set to Public'}
                </button>
        </form> 
        """ for row in reviewData])

        return f'''<h2>Welcome to the review manager</h2>
                    Here you can accept or reject reviews here.<br><br>
                   {formatted_reviews}
                   <br><br>
                   <a href="/employeePortal">Return</a>''', 200

    except Exception as e:
        return jsonify({'Error': str(e)})

    finally:
        try:
            if cursor:
                cursor.close()
            if connect:
                connect.close()
        except Exception as e:
            # Optionally log any errors related to closing
            print(f"Error closing connection: {e}")

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
