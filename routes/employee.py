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
        # Connect the cursor to the database
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
                session['ID'] = employee[0]
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

@employeeBP.route('/logout')
def logout():
    session ['loggedIn'] = False
    session.pop('username', None)
    session.pop('ID', None)
    return redirect(url_for('home.home'))