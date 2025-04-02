from flask import Blueprint, request, render_template, redirect, url_for, session, jsonify
from databaseModule import connect_to_db

estimateManagerBP = Blueprint('estimateManager', __name__)

@estimateManagerBP.route('/estimateManager', methods=['GET', 'POST'])
def estimateManager():
    if not session.get('loggedIn'):  # extremely important as this prevents non authorized users from accessing pages by simply writing in url
        return redirect(url_for('employee.employeeLogin'))

    try:
        connect = connect_to_db()
        cursor = connect.cursor()
        cursor.execute('SELECT "NAME", "PHONE", "EMAIL", "DATE", "DESCRIPTION", "ADDRESS", "CITY", "ZIP_CODE", "PRIMARY_KEY", "HANDLED" FROM "ESTIMATES"')
        requestData = cursor.fetchall()

        print("Query executed successfully")

        open_requests = []
        closed_requests = []

        for row in requestData:
            formatted_request = f'''
                        <div class="request-item">
                            <strong>Request ID:</strong> {row[8]}<br>
                            <strong>Date:</strong> {row[3]}<br>
                            <strong>Name:</strong> {row[0]}<br>
                            <strong>Phone:</strong> {row[1]}<br>
                            <strong>Email:</strong> {row[2]}<br>
                            <strong>Address:</strong> {row[5]}, {row[6]}, {row[7]}<br>
                            <strong>Description:</strong> {row[4]}<br>
                            {'' if row[9] else f'<form method="POST" action="/markHandled"><input type="hidden" name="request_id" value="{row[8]}"><button type="submit">Mark as Handled</button></form>'}
                        </div>
                    '''

            if row[9]:
                closed_requests.append(formatted_request)
            else:
                open_requests.append(formatted_request)

        return render_template("estimateManager.html", open_requests=open_requests, closed_requests=closed_requests)

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

@estimateManagerBP.route('/markHandled/', methods=['POST'])
def markHandled():
    if not session.get('loggedIn'):
        return redirect(url_for('employee.employeeLogin'))

    try:
        request_id = request.form.get('request_id')
        connect = connect_to_db()
        cursor = connect.cursor()
        cursor.execute('UPDATE "ESTIMATES" SET "HANDLED" = TRUE WHERE "PRIMARY_KEY" = %s', (request_id,))
        connect.commit()
        return redirect(url_for('employee.estimateManager'))

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


