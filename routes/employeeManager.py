from flask import Blueprint, request, render_template, redirect, url_for, session, jsonify
from databaseModule import connect_to_db

employeeManagerBP = Blueprint('employeeManager', __name__)

@employeeManagerBP.route('/employeeManager', methods=['GET', 'POST'])
def employeeManager():
    if not session.get('loggedIn'): #extremely important as this prevents non authorized users from accessing pages by simplying writing in url
        return redirect(url_for('employee.employeeLogin'))

    username = session.get('username')
    if 'verifiedAdministrator' not in session:
        if request.method == 'POST':
            password = request.form.get('password')

            if not password:
                return "Must enter a password"

            connect = connect_to_db()
            cursor = connect.cursor()

            try:
                cursor.execute('SELECT * FROM "EMPLOYEE_CREDENTIALS" WHERE "EMPLOYEE_USERNAME" = %s AND "EMPLOYEE_PASSWORD" = %s AND "ADMIN" = %s',
                (username, password, True))
                employee = cursor.fetchone()

                if employee:
                    session['verifiedAdministrator'] = True
                    return redirect(url_for('employeeManager'))
                else:
                    return'''Invalid credentials or you are not an authorized administrator.<br>
                    <a href="/resetUsername">Return</a>'''

            finally:
                cursor.close()
                connect.close()

        return """
        <form method="POST">
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required><br><br>
            <input type="submit" value="Submit">
            <a href="/employeePortal">Return</a>
        </form>
        """