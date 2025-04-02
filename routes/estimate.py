from flask import Blueprint, request, render_template, redirect, url_for, session, jsonify
from app import currentTime
from databaseModule import connect_to_db
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

estimateBP = Blueprint('estimate', __name__)

@estimateBP.route('/requestEstimate', methods=['GET', 'POST'])
def requestEstimate():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        description = request.form.get('description')
        address = request.form.get('address')
        city = request.form.get('city')
        zipCode = request.form.get('zipCode')
        date = currentTime

        if not name or not phone:
            return "Fields with '*' are required.", 400

        try:
            connect = connect_to_db()
            cursor = connect.cursor()

            cursor.execute('INSERT INTO "ESTIMATES" ("NAME", "PHONE", "EMAIL", "DATE", "DESCRIPTION", "ADDRESS","CITY", "ZIP_CODE") VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING "PRIMARY_KEY"',
                            (name, phone, email, date, description, address, city, zipCode))

            requestID = cursor.fetchone()[0]
            connect.commit()

            cursor.execute('SELECT * FROM "ESTIMATES" WHERE "PRIMARY_KEY" = %s', (requestID,))
            requestData = cursor.fetchone()

            sendEstimateRequestEmail(requestData)

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

    return render_template('estimateForm.html')

def sendEstimateRequestEmail(requestData, recipientEmail="denheyerhelper@gmail.com"):
    senderEmail = "denheyerhelper@gmail.com"
    senderPassword = "ehiq crry clwx mlrl"

    #DenHeyerElectricEmailBot2025 is the gmail accounts password

    subject = f"New Estimate Request: {requestData[0]}"

    body = f"""
    A new estimate request has been submitted.<br>
    Request ID: {requestData[0]}
    Date: {requestData[4]}
    Name: {requestData[1]}
    Phone: {requestData[2]}
    Email: {requestData[3]}
    Address: {requestData[6]}, {requestData[7]}, {requestData[8]}
    Description: {requestData[5]}
    """

    msg = MIMEMultipart()
    msg['From'] = senderEmail
    msg['To'] = recipientEmail
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(senderEmail, senderPassword)
        server.sendmail(senderEmail, recipientEmail, msg.as_string())
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"Error sending email: {e}")