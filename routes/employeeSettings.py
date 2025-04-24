from flask import Blueprint, request, redirect, url_for, session
from databaseModule import connect_to_db

employeeSettingsBP = Blueprint('employeeSettings', __name__)


@employeeSettingsBP.route('/employeeSettings')
def employeeSettings():
    if not session.get('loggedIn'):
        return redirect(url_for('employee.employeeLogin'))

    ID = session.get('ID')

    connect = connect_to_db()
    cursor = connect.cursor()

    try:
        cursor.execute('SELECT "EMAIL_LIST" FROM "EMPLOYEE_CREDENTIALS" WHERE "PRIMARY_KEY" = %s', (ID,))
        subscribed = cursor.fetchone()[0]  # should return True or False

        button_label = "Unsubscribe from Emails" if subscribed else "Subscribe to Emails"
        status_message = "You are currently subscribed to estimate emails." if subscribed else "You are not subscribed to estimate emails."

        return f'''
            <h2>Employee Settings</h2>
            <ul>
                <li><a href="/resetUsername">Reset Username</a></li>
                <li><a href="/resetPassword">Reset Password</a></li>
            </ul>

            <p>{status_message}</p>
            <form method="POST" action="/emailList">
                <button type="submit">{button_label}</button>
            </form>
            '''
    finally:
        cursor.close()
        connect.close()

@employeeSettingsBP.route('/resetPassword', methods=['GET', 'POST'])
def resetPassword():
    if not session.get('loggedIn'): #extremely important as this prevents non authorized users from accessing pages by simplying writing in url
        return redirect(url_for('employee.employeeLogin'))

    username = session.get('username')
    if 'verified' not in session:
        if request.method == 'POST':
            password = request.form.get('password')

            if not password:
                return "Must enter a password"

            connect = connect_to_db()
            cursor = connect.cursor()

            try:
                cursor.execute('SELECT * FROM "EMPLOYEE_CREDENTIALS" WHERE "EMPLOYEE_USERNAME" = %s AND "EMPLOYEE_PASSWORD" = %s',
                (username, password))
                employee = cursor.fetchone()

                if employee:
                    session['verified'] = True
                    return redirect(url_for('employeeSettings.resetPassword'))
                else:
                    return'''Invalid credentials. Please try again.<br>
                    <a href="/resetPassword">Return</a>'''

            finally:
                cursor.close()
                connect.close()

        return """
        <form method="POST">
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required><br><br>
            <input type="submit" value="Submit">
            <a href="/">Return</a>
        </form>
        """

    else:
        if request.method == 'POST':
            username = session.get('username')
            password1 = request.form.get('password1')
            password2 = request.form.get('password2')

            if not password1 or not password2:
                return '''Must enter password <br>
                        <a href="/resetPassword">Return</a>'''

            if password1 != password2:
                return """Passwords don't match <br>
                        <a href="/resetPassword">Return</a>
                        """

            connect = connect_to_db()
            cursor = connect.cursor()
            try:
                cursor.execute('UPDATE "EMPLOYEE_CREDENTIALS" SET "EMPLOYEE_PASSWORD" = %s WHERE "EMPLOYEE_USERNAME" = %s', (password1, username))
                connect.commit()

            finally:
                cursor.close()
                connect.close()
                session.pop('verified', None)

            return'''Password successfully changed
            <a href="/employeePortal">Return</a>
            '''

        return """
        <form method="POST">
            <label for="password1">New Password:</label>
            <input type="password" id="password1" name="password1" required><br><br>
            <label for="password2">Confirm New Password:</label>
            <input type="password" id="password2" name="password2" required><br><br>
            <input type="submit" value="Submit">
        """

@employeeSettingsBP.route('/resetUsername', methods=['GET', 'POST'])
def resetUsername():
    if not session.get('loggedIn'): #extremely important as this prevents non authorized users from accessing pages by simplying writing in url
        return redirect(url_for('employee.employeeLogin'))

    username = session.get('username')
    if 'verifiedUsernameChange' not in session:
        if request.method == 'POST':
            password = request.form.get('password')

            if not password:
                return "Must enter a password"

            connect = connect_to_db()
            cursor = connect.cursor()

            try:
                cursor.execute('SELECT * FROM "EMPLOYEE_CREDENTIALS" WHERE "EMPLOYEE_USERNAME" = %s AND "EMPLOYEE_PASSWORD" = %s',
                (username, password))
                employee = cursor.fetchone()

                if employee:
                    session['verifiedUsernameChange'] = True
                    return redirect(url_for('employeeSettings.resetUsername'))
                else:
                    return'''Invalid credentials. Please try again.<br>
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

    else:
        if request.method == 'POST':
            username = session.get('username')
            newUsername1 = request.form.get('newUsername1')
            newUsername2 = request.form.get('newUsername2')

            if not newUsername1 or not newUsername2:
                return '''Must enter username <br>
                        <a href="/resetUsername">Return</a>'''

            if newUsername1 != newUsername2:
                return '''Usernames don't match <br>
                        <a href="/resetUsername">Return</a>
                        '''

            connect = connect_to_db()
            cursor = connect.cursor()
            try:
                cursor.execute('UPDATE "EMPLOYEE_CREDENTIALS" SET "EMPLOYEE_USERNAME" = %s WHERE "EMPLOYEE_USERNAME" = %s', (newUsername1, username))
                connect.commit()

            finally:
                cursor.close()
                connect.close()
                session['username'] = newUsername1
                session.pop('verifiedUsernameChange', None)

            return'''Username successfully changed
            <a href="/employeePortal">Return</a>
            '''

        return """
        <form method="POST">
            <label for="newUsername1">New Username:</label>
            <input type="text" id="newUsername1" name="newUsername1" required><br><br>
            <label for="newUsername2">Confirm New Username:</label>
            <input type="text" id="newUsername2" name="newUsername2" required><br><br>
            <input type="submit" value="Submit">
        """
@employeeSettingsBP.route('/emailList', methods=['GET', 'POST'])
def emailList():
    if not session.get('loggedIn'): return redirect(url_for('employee.employeeLogin'))

    connect = connect_to_db()
    cursor = connect.cursor()
    ID=session.get('ID')

    try:
        cursor.execute('UPDATE "EMPLOYEE_CREDENTIALS" SET "EMAIL_LIST" = NOT "EMAIL_LIST" WHERE "PRIMARY_KEY" = %s',(ID,))
        connect.commit()
        return redirect(url_for('employeeSettings.employeeSettings'))

    except Exception as e:
        return f"An error occurred: {e}"

    finally:
        cursor.close()
        connect.close()
