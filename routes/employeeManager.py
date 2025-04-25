from flask import Blueprint, request, render_template, redirect, url_for, session, jsonify, flash
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

            connect = connect_to_db()
            cursor = connect.cursor()

            try:
                cursor.execute('SELECT * FROM "EMPLOYEE_CREDENTIALS" WHERE "EMPLOYEE_USERNAME" = %s AND "EMPLOYEE_PASSWORD" = %s AND "ADMIN" = %s',
                (username, password, True))
                employee = cursor.fetchone()

                if employee:
                    session['verifiedAdministrator'] = True
                    return redirect(url_for('employeeManager.employeeManager'))
                else:
                    flash("Invalid credentials. Please try again.")
                    return redirect(url_for('employeeSettings.resetPassword'))

            finally:
                cursor.close()
                connect.close()

        return render_template('verifyPassword.html')


    else:
        try:
            connect = connect_to_db()
            cursor = connect.cursor()

            cursor.execute('SELECT "EMPLOYEE_NAME", "EMPLOYEE_USERNAME", "EMPLOYEE_EMAIL", "ADMIN", "PRIMARY_KEY" FROM "EMPLOYEE_CREDENTIALS" ',)
            employeeData = cursor.fetchall()

            return render_template("employeeManager.html", employeeData=employeeData)

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

@employeeManagerBP.route('/addUser', methods=['GET', 'POST'])
def addUser():
    if 'verifiedAdministrator' not in session:
        return redirect(url_for('employee.employeePortal'))

    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if not name or not username or not email or not password:
            return "All fields required", 400

        try:
            connect = connect_to_db()
            cursor = connect.cursor()

            cursor.execute('INSERT INTO "EMPLOYEE_CREDENTIALS" ("EMPLOYEE_NAME", "EMPLOYEE_USERNAME", "EMPLOYEE_EMAIL", "EMPLOYEE_PASSWORD") VALUES (%s, %s, %s, %s)',
                            (name, username, email, password))
            connect.commit()

            return redirect(url_for("employeeManager.employeeManager"))

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

    return render_template('addNewUser.html')

@employeeManagerBP.route('/removeUser/<int:primaryKey>', methods=['POST'])
def removeUser(primaryKey):
    if 'verifiedAdministrator' not in session:
        return redirect(url_for('employee.employeePortal'))

    connect = connect_to_db()
    cursor = connect.cursor()

    try:
        cursor.execute('DELETE FROM "EMPLOYEE_CREDENTIALS" WHERE "PRIMARY_KEY" = %s', (primaryKey,))
        connect.commit()
    finally:
        try:
            if cursor:
                cursor.close()
            if connect:
                connect.close()
        except Exception as e:
            print(f"Error closing connection: {e}")

    return redirect(url_for('employeeManager.employeeManager'))

@employeeManagerBP.route('/toggleAdmin/<int:primaryKey>', methods=['POST'])
def toggleAdmin(primaryKey):
    if 'verifiedAdministrator' not in session:
        return redirect(url_for('employee.employeePortal'))

    try:
        connect = connect_to_db()
        cursor = connect.cursor()

        cursor.execute(''' UPDATE "EMPLOYEE_CREDENTIALS" SET "ADMIN" = NOT "ADMIN" WHERE "PRIMARY_KEY" = %s ''', (primaryKey,))
        connect.commit()

    except Exception as e:
        return jsonify({'Error': str(e)})

    finally:
        if cursor:
            cursor.close()
        if connect:
            connect.close()

    return redirect(url_for('employeeManager.employeeManager'))

@employeeManagerBP.before_app_request
def clearVerification():
    if 'verifiedAdministrator' not in session:
        return
    if session.get('verifiedAdministrator') and request.endpoint == 'employeeManager.employeeManager' or request.endpoint == 'employeeManager.addUser' or request.endpoint == 'employeeManager.removeUser' or request.endpoint == 'employeeManager.toggleAdmin':
        return
    else:
        session.pop('verifiedAdministrator')