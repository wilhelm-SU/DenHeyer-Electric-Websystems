from flask import Blueprint, request, render_template, redirect, url_for, session, jsonify
from databaseModule import connect_to_db

estimateManagerBP = Blueprint('estimateManager', __name__)

@estimateManagerBP.route('/estimateManager/open', methods=['GET', 'POST'])
def estimateManagerOpen():
    if not session.get('loggedIn'):
        return redirect(url_for('employee.employeeLogin'))


    try:
        connect = connect_to_db()
        cursor = connect.cursor()
        cursor.execute('SELECT "NAME", "PHONE", "EMAIL", "DATE", "DESCRIPTION", "ADDRESS", "CITY", "ZIP_CODE", "PRIMARY_KEY", "HANDLED" FROM "ESTIMATES"')
        requestData = cursor.fetchall()

        open_requests = []
        for row in requestData:
            if not row[9]:  # HANDLED is False (open)
                markHandledForm = f'''
                    <form method="POST" action="/markHandled" onsubmit="return confirm('Are you sure you want to mark this estimate as handled?');" style="display:inline;">
                        <input type="hidden" name="request_id" value="{row[8]}">
                        <button type="submit">Mark as Handled</button>
                    </form>
                '''

                formattedRequest = f'''
                    <div class="request-item">
                        <strong>Request ID:</strong> {row[8]}<br>
                        <strong>Date:</strong> {row[3]}<br>
                        <strong>Name:</strong> {row[0]}<br>
                        <strong>Phone:</strong> {row[1]}<br>
                        <strong>Email:</strong> {row[2]}<br>
                        <strong>Address:</strong> {row[5]}, {row[6]}, {row[7]}<br>
                        <strong>Description:</strong> {row[4]}<br>
                        {markHandledForm}
                        <form method="POST" action="/deleteEstimate/" onsubmit="return confirm('Are you sure you want to delete this estimate?');" style="display:inline;">
                            <input type="hidden" name="request_id" value="{row[8]}">
                            <button type="submit">Delete</button>
                        </form>
                    </div>
                '''
                open_requests.append(formattedRequest)

        page = int(request.args.get('page', 1))
        per_page = 5
        total = len(open_requests)
        total_pages = (total + per_page - 1) // per_page
        start = (page - 1) * per_page
        end = start + per_page
        paginated_requests = open_requests[start:end]

        return render_template("estimateManagerOpen.html", open_requests=paginated_requests, page=page, total_pages=total_pages)

    except Exception as e:
        return jsonify({'Error': str(e)})
    finally:
        if cursor: cursor.close()
        if connect: connect.close()

@estimateManagerBP.route('/estimateManager/closed', methods=['GET', 'POST'])
def estimateManagerClosed():
    if not session.get('loggedIn'):
        return redirect(url_for('employee.employeeLogin'))

    try:
        connect = connect_to_db()
        cursor = connect.cursor()
        cursor.execute('SELECT "NAME", "PHONE", "EMAIL", "DATE", "DESCRIPTION", "ADDRESS", "CITY", "ZIP_CODE", "PRIMARY_KEY", "HANDLED" FROM "ESTIMATES"')
        requestData = cursor.fetchall()

        closed_requests = []
        for row in requestData:
            if row[9]:  # HANDLED is True (closed)
                formattedRequest = f'''
                    <div class="request-item">
                        <strong>Request ID:</strong> {row[8]}<br>
                        <strong>Date:</strong> {row[3]}<br>
                        <strong>Name:</strong> {row[0]}<br>
                        <strong>Phone:</strong> {row[1]}<br>
                        <strong>Email:</strong> {row[2]}<br>
                        <strong>Address:</strong> {row[5]}, {row[6]}, {row[7]}<br>
                        <strong>Description:</strong> {row[4]}<br>
                        <form method="POST" action="/deleteEstimate/" onsubmit="return confirm('Are you sure you want to delete this estimate?');" style="display:inline;">
                            <input type="hidden" name="request_id" value="{row[8]}">
                            <button type="submit">Delete</button>
                        </form>
                    </div>
                '''
                closed_requests.append(formattedRequest)

        page = int(request.args.get('page', 1))
        per_page = 10
        total = len(closed_requests)
        total_pages = (total + per_page - 1) // per_page
        start = (page - 1) * per_page
        end = start + per_page
        paginated_requests = closed_requests[start:end]

        return render_template("estimateManagerClosed.html", closed_requests=paginated_requests, page=page, total_pages=total_pages)

    except Exception as e:
        return jsonify({'Error': str(e)})
    finally:
        if cursor: cursor.close()
        if connect: connect.close()

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
        return redirect(url_for('estimateManager.estimateManagerOpen'))

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
        return redirect(url_for('estimateManager.estimateManagerOpen'))

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

@estimateManagerBP.route('/searchOpen/', methods=['GET'])
def search_open():
    if not session.get('loggedIn'):
        return redirect(url_for('employee.employeeLogin'))

    searchQuery = request.args.get('query', '').strip()

    try:
        connect = connect_to_db()
        cursor = connect.cursor()
        cursor.execute('''SELECT "NAME", "PHONE", "EMAIL", "DATE", "ADDRESS", "DESCRIPTION", "CITY", "ZIP_CODE", "PRIMARY_KEY", "HANDLED" FROM "ESTIMATES"
                          WHERE "HANDLED" = FALSE
                          AND(
                             "NAME" ILIKE %s
                          OR "PHONE" ILIKE %s
                          OR "EMAIL" ILIKE %s
                          OR CAST("DATE" AS TEXT) ILIKE %s
                          OR "ADDRESS" ILIKE %s
                          OR "CITY" ILIKE %s
                          OR "ZIP_CODE" ILIKE %s
                          OR CAST("PRIMARY_KEY" as TEXT) ILIKE %s 
                          )
                       ''', tuple(['%' + searchQuery + '%'] * 8))

        requestData = cursor.fetchall()
        searchResults = []

        for row in requestData:
            markHandledForm = ''
            if not row[9]:
                markHandledForm = f'''
                    <form method="POST" action="/markHandled">
                        <input type="hidden" name="request_id" value="{row[8]}">
                        <button type="submit">Mark as Handled</button>
                    </form>
                '''

            formattedRequest = f'''
                <div class="request-item">
                    <strong>Request ID:</strong> {row[8]}<br>
                    <strong>Date:</strong> {row[3]}<br>
                    <strong>Name:</strong> {row[0]}<br>
                    <strong>Phone:</strong> {row[1]}<br>
                    <strong>Email:</strong> {row[2]}<br>
                    <strong>Address:</strong> {row[5]}, {row[6]}, {row[7]}<br>
                    <strong>Description:</strong> {row[4]}<br>
                    {markHandledForm}
                </div>
            '''

            searchResults.append(formattedRequest)

        return render_template("estimateManagerOpen.html", searchResults = searchResults, searchQuery = searchQuery)

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

@estimateManagerBP.route('/searchClosed/', methods=['GET'])
def search_closed():
    if not session.get('loggedIn'):
        return redirect(url_for('employee.employeeLogin'))

    searchQuery = request.args.get('query', '').strip()

    try:
        connect = connect_to_db()
        cursor = connect.cursor()
        cursor.execute('''SELECT "NAME", "PHONE", "EMAIL", "DATE", "ADDRESS", "DESCRIPTION", "CITY", "ZIP_CODE", "PRIMARY_KEY", "HANDLED" FROM "ESTIMATES"
                          WHERE "HANDLED" = TRUE
                          AND(
                             "NAME" ILIKE %s
                          OR "PHONE" ILIKE %s
                          OR "EMAIL" ILIKE %s
                          OR CAST("DATE" AS TEXT) ILIKE %s
                          OR "ADDRESS" ILIKE %s
                          OR "CITY" ILIKE %s
                          OR "ZIP_CODE" ILIKE %s
                          OR CAST("PRIMARY_KEY" as TEXT) ILIKE %s 
                          )
                       ''', tuple(['%' + searchQuery + '%'] * 8))

        requestData = cursor.fetchall()
        searchResults = []

        for row in requestData:
            markHandledForm = ''
            if not row[9]:
                markHandledForm = f'''
                    <form method="POST" action="/markHandled">
                        <input type="hidden" name="request_id" value="{row[8]}">
                        <button type="submit">Mark as Handled</button>
                    </form>
                '''

            formattedRequest = f'''
                <div class="request-item">
                    <strong>Request ID:</strong> {row[8]}<br>
                    <strong>Date:</strong> {row[3]}<br>
                    <strong>Name:</strong> {row[0]}<br>
                    <strong>Phone:</strong> {row[1]}<br>
                    <strong>Email:</strong> {row[2]}<br>
                    <strong>Address:</strong> {row[5]}, {row[6]}, {row[7]}<br>
                    <strong>Description:</strong> {row[4]}<br>
                    {markHandledForm}
                </div>
            '''

            searchResults.append(formattedRequest)

        return render_template("estimateManagerClosed.html", searchResults = searchResults, searchQuery = searchQuery)

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