from flask import Blueprint, request, redirect, url_for, session, render_template, flash
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

        return render_template('employeeSettings.html', button_label=button_label, status_message=status_message)

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
                    flash("Invalid credentials. Please try again.")
                    return redirect(url_for('employeeSettings.resetPassword'))

            finally:
                cursor.close()
                connect.close()

        return render_template('verifyPassword.html')

    else:
        if request.method == 'POST':
            username = session.get('username')
            password1 = request.form.get('password1')
            password2 = request.form.get('password2')

            if password1 != password2:
                    flash("Passwords do not match. Please try again.")
                    return redirect(url_for('employeeSettings.resetPassword'))

            connect = connect_to_db()
            cursor = connect.cursor()
            try:
                cursor.execute('UPDATE "EMPLOYEE_CREDENTIALS" SET "EMPLOYEE_PASSWORD" = %s WHERE "EMPLOYEE_USERNAME" = %s', (password1, username))
                connect.commit()

            finally:
                cursor.close()
                connect.close()
                session.pop('verified', None)

            return redirect(url_for('employeeSettings.employeeSettings'))


        return render_template('resetPassword.html')

@employeeSettingsBP.route('/resetUsername', methods=['GET', 'POST'])
def resetUsername():
    if not session.get('loggedIn'): #extremely important as this prevents non authorized users from accessing pages by simplying writing in url
        return redirect(url_for('employee.employeeLogin'))

    username = session.get('username')
    if 'verifiedUsernameChange' not in session:
        if request.method == 'POST':
            password = request.form.get('password')

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
                    flash("Invalid credentials. Please try again.")
                    return redirect(url_for('employeeSettings.resetPassword'))

            finally:
                cursor.close()
                connect.close()

        return render_template('verifyPassword.html')

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

            return redirect(url_for('employeeSettings.employeeSettings'))

        return render_template('resetUsername.html')

@employeeSettingsBP.route('/resetEmail', methods=['GET', 'POST'])
def resetEmail():
    if not session.get('loggedIn'): #extremely important as this prevents non authorized users from accessing pages by simplying writing in url
        return redirect(url_for('employee.employeeLogin'))


    if 'verifiedEmailChange' not in session:
        if request.method == 'POST':
            password = request.form.get('password')


            connect = connect_to_db()
            cursor = connect.cursor()

            ID = session.get('ID')

            try:
                cursor.execute('SELECT * FROM "EMPLOYEE_CREDENTIALS" WHERE "PRIMARY_KEY" = %s AND "EMPLOYEE_PASSWORD" = %s',
                (ID, password))
                employee = cursor.fetchone()

                if employee:
                    session['verifiedEmailChange'] = True
                    return redirect(url_for('employeeSettings.resetEmail'))
                else:
                    flash("Invalid credentials. Please try again.")
                    return redirect(url_for('employeeSettings.resetPassword'))

            finally:
                cursor.close()
                connect.close()

        return render_template('verifyPassword.html')

    else:
        if request.method == 'POST':
            ID = session.get('ID')
            newEmail1 = request.form.get('newEmail1')
            newEmail2 = request.form.get('newEmail2')


            if newEmail1 != newEmail2:
                return '''Emails don't match <br>
                        <a href="/resetEmail">Return</a>
                        '''

            connect = connect_to_db()
            cursor = connect.cursor()
            try:
                cursor.execute('UPDATE "EMPLOYEE_CREDENTIALS" SET "EMPLOYEE_EMAIL" = %s WHERE "PRIMARY_KEY" = %s', (newEmail1, ID))
                connect.commit()

            finally:
                cursor.close()
                connect.close()
                session.pop('verifiedEmailChange', None)

            return redirect(url_for('employeeSettings.employeeSettings'))

        return render_template('resetEmail.html')
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

@employeeSettingsBP.before_app_request
def clearVerification():
    if 'verifiedUsernameChange' or 'verified' not in session:
        return
    if session.get('verifiedUsernameChange') and request.endpoint == 'employeeSettings.resetUsername' or request.endpoint == 'employeeSettings.resetPassword':
        return
    if session.get('verified') and request.endpoint == 'employeeSettings.resetUsername' or request.endpoint == 'employeeSettings.resetPassword':
        return
    else:
        session.pop('verifiedUsernameChange')
        session.pop('verified')
        return
