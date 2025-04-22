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
            formattedRequest = f'''
                        <div class="request-item">
                            <strong>Request ID:</strong> {row[8]}<br>
                            <strong>Date:</strong> {row[3]}<br>
                            <strong>Name:</strong> {row[0]}<br>
                            <strong>Phone:</strong> {row[1]}<br>
                            <strong>Email:</strong> {row[2]}<br>
                            <strong>Address:</strong> {row[5]}, {row[6]}, {row[7]}<br>
                            <strong>Description:</strong> {row[4]}<br>
                            {''
                            if row[9] else f'''
                                <form method="POST" action="/markHandled" onsubmit="return confirm('Are you sure you want to mark this estimate as handled?');" style="display:inline;">
                                    <input type="hidden" name="request_id" value="{row[8]}">
                                    <button type="submit">Mark as Handled</button>
                                </form>
                            '''}
                            <form method="POST" action="/deleteEstimate/" onsubmit="return confirm('Are you sure you want to delete this estimate?');" style="display:inline;">
                                <input type="hidden" name="request_id" value="{row[8]}">
                                <button type="submit">Delete</button>
                            </form>
                        </div>
                    '''

            if row[9]:
                closed_requests.append(formattedRequest)
            else:
                open_requests.append(formattedRequest)

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
        return redirect(url_for('estimateManager.estimateManager'))

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

@estimateManagerBP.route('/deleteEstimate/', methods=['POST'])
def deleteEstimate():
    if not session.get('loggedIn'):
        return redirect(url_for('employee.employeeLogin'))

    try:
        request_id = request.form.get('request_id')
        connect = connect_to_db()
        cursor = connect.cursor()
        cursor.execute('DELETE FROM "ESTIMATES" WHERE "PRIMARY_KEY" = %s', (request_id,))
        connect.commit()
        return redirect(url_for('estimateManager.estimateManager'))

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

@estimateManagerBP.route('/search/', methods=['GET'])
def search():
    if not session.get('loggedIn'):
        return redirect(url_for('employee.employeeLogin'))

    searchQuery = request.args.get('query', '').strip()

    try:
        connect = connect_to_db()
        cursor = connect.cursor()
        cursor.execute('''SELECT "NAME", "PHONE", "EMAIL", "DATE", "ADDRESS", "DESCRIPTION", "CITY", "ZIP_CODE", "PRIMARY_KEY", "HANDLED" FROM "ESTIMATES"
                          WHERE "NAME" ILIKE %s
                          OR "PHONE" ILIKE %s
                          OR "EMAIL" ILIKE %s
                          OR CAST("DATE" AS TEXT) ILIKE %s
                          OR "ADDRESS" ILIKE %s
                          OR "CITY" ILIKE %s
                          OR "ZIP_CODE" ILIKE %s
                          OR CAST("PRIMARY_KEY" as TEXT) ILIKE %s 
                       ''', tuple(['%' + searchQuery + '%'] * 8))

        requestData = cursor.fetchall()
        searchResults = []

        for row in requestData:
            formattedRequest = f'''
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

            searchResults.append(formattedRequest)

        return render_template("estimateManager.html", searchResults = searchResults, searchQuery = searchQuery)

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


