from flask import Blueprint, request, render_template, redirect, url_for, session, jsonify
from app import currentTime
from databaseModule import connect_to_db

estimateBP = Blueprint('estimate', __name__)

@estimateBP.route('/requestEstimate', methods=['GET', 'POST'])
def requestEstimate():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        description = request.form.get('description')
        address = request.form.get('address')
        date = currentTime()

        if not name or not phone:
            return "Name, phone, address and description fields required.", 400

        try:
            try:
                connect = connect_to_db()
                cursor = connect.cursor()

                cursor.execute('INSERT INTO "ESTIMATES" ("NAME", "PHONE", "EMAIL", "DESCRIPTION", "ADDRESS", "DATE") VALUES (%s, %s, %s, %s, %s, %s)',
                               (name, phone, email, description, address, date))
                connect.commit()

                return '''
                    Thank you for submitting an estimate request, a DenHeyer Electric associate will contact you within your allotted times<br>
                    <a href="/">Return Home</a>
                    '''

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

    return render_template('')