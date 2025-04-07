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


#Gotta work on adding to the employeePortal.html because the raw image data is not being formated
#to what the actual image should be
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

            """ for row in image_list])

        return f'''<h2>Welcome to the gallery manager</h2>
                    Here you can accept or reject images from being displayed
                    in the public gallery.<br><br>
                    {formatted_gallery}
                    <br><br>
                    <a href="/employeePortal">Return</a>''', 200

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



@employeeBP.route('/logout')
def logout():
    session ['loggedIn'] = False
    return redirect(url_for('employee.employeeLogin'))