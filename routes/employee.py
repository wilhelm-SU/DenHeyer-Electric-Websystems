from flask import Blueprint, request, render_template, redirect, url_for, session, jsonify
from databaseModule import connect_to_db

employeeBP = Blueprint('employee', __name__)

@employeeBP.route('/employeeLogin', methods=['GET', 'POST'])
def employeeLogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            return "Both fields are required.", 400

        try:
            connect = connect_to_db()
            cursor = connect.cursor()

            # Check if credentials exist in the database
            cursor.execute('SELECT * FROM "EMPLOYEE_CREDENTIALS" WHERE "EMPLOYEE_USERNAME" = %s AND "EMPLOYEE_PASSWORD" = %s',
                           (username, password))
            employee = cursor.fetchone()

            if employee:
                session['loggedIn'] = True
                session['username'] = username
                return redirect(url_for('employee.employeePortal'))  # Redirect to the employee portal
            else:
                return ('''Invalid credentials. Please try again.<br>
                        "<a href="/employeeLogin">Return</a><br>''', 401)

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

    # Render login form
    return render_template('employeeLoginForm.html')

@employeeBP.route('/employeePortal')
def employeePortal():
    if not session.get('loggedIn'): #extremely important as this prevents non authorized users from accessing pages by simplying writing in url
        return redirect(url_for('employee.employeeLogin'))

    username = session.get('username')
    return render_template('employeePortal.html', username=username)

@employeeBP.route('/reviewManager', methods=['GET', 'POST'])
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

@employeeBP.route('/togglePublic/<key>', methods=['POST'])
def togglePublic(key):
    connect = connect_to_db()
    cursor = connect.cursor()

    cursor.execute('SELECT "PUBLIC" FROM "REVIEWS" WHERE "PRIMARY_KEY" = %s', (key,))
    currentStatus = cursor.fetchone()[0]
    newStatus = not currentStatus

    cursor.execute('UPDATE "REVIEWS" SET "PUBLIC" = %s WHERE "PRIMARY_KEY" = %s', (newStatus, key))

    connect.commit()

    return redirect(url_for('employee.reviewManager'))

@employeeBP.route('/resetPassword', methods=['GET', 'POST'])
def resetPassword():
    if not session.get('loggedIn'): #extremely important as this prevents non authorized users from accessing pages by simplying writing in url
        return redirect(url_for('employee.employeeLogin'))
    return ''

@employeeBP.route('/logout')
def logout():
    session ['loggedIn'] = False
    return redirect(url_for('employee.employeeLogin'))