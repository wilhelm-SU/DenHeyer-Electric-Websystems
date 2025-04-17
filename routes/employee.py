import base64
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

#route for gallery manager
@employeeBP.route('/galleryManager', methods=['GET', 'POST'])
def galleryManager():
    if not session.get('loggedIn'):  # extremely important as this prevents non authorized users from accessing pages by simply writing in url
        return redirect(url_for('employee.employeeLogin'))

    try:
        connect = connect_to_db()
        cursor = connect.cursor()
        cursor.execute('SELECT "PRIMARY_KEY", "IMAGE_DATA", "DESCRIPTION", "PUBLIC" FROM "GALLERY" ORDER BY "PRIMARY_KEY" ASC')
        print("Query executed successfully")

        imageData = cursor.fetchall()

        image_list = []
        for data in imageData:
            if data[1]:
                base64_imageData = base64.b64encode(data[1]).decode('utf-8')
                image_list.append((data[0], base64_imageData, data[2], data[3]))

        if not image_list:
            return '''No images available.<br>'''

        formatted_gallery = "<br><br>".join(
            [f"""
            <strong>Image:</strong><br>
            <img src="data:image/jpeg;base64,{row[1]}" alt="Gallery Image" style="max-width: 300px; max-height: 300px;"><br><br>
            <strong>Description:</strong>{row[2]}<br><br>
            <strong>Publicly displayed:</strong>{row[3]}<br><br>
            <form action="/togglePublic/{row[0]}" method="POST">
                <input type="hidden" name="table" value="GALLERY">
                <button type="submit">
                    {'Set to Private' if row[3] else 'Set to Public'}
                </button>
            </form>

            <form action="/deleteImage/{row[0]}" method="POST" style="display:inline; margin-left: 10px;">
                <input type="hidden" name="table" value="GALLERY">
                <button type="submit" onclick="return confirm('Are you sure you want to delete this image?');">
                    Delete
                </button>
            </form>

            """ for row in image_list])

        #funtion to delete an image from the gallery in the database


        return f'''<h2>Welcome to the gallery manager</h2>
                    Here you can accept or reject images from being displayed
                    in the public gallery.<br><br>
                    <a href="/insertImagePage">Add New Image</a>
                    {formatted_gallery}
                    <br><br>
                    <a href="/employeePortal">Return</a>''', 200
        #/galleryManagerManipulation/insertImagePage

        print(imageData)
        print('why is there an error bellow?')

    finally:
        try:
            if cursor:
                cursor.close()
            if connect:
                connect.close()
        except Exception as e:
            # Optionally log any errors related to closing
            print(f"Error closing connection: {e}")


@employeeBP.route('/resetPassword', methods=['GET', 'POST'])
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
                    return redirect(url_for('employee.resetPassword'))
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

@employeeBP.route('/resetUsername', methods=['GET', 'POST'])
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
                    return redirect(url_for('employee.resetUsername'))
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

@employeeBP.route('/logout')
def logout():
    session ['loggedIn'] = False
    return redirect(url_for('home.home'))