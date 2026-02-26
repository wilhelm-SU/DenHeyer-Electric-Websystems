import os

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

        if not name or not phone or not address or not city or not zipCode:
            return "Fields with '*' are required.", 400


        try:
            connect = connect_to_db()
            cursor = connect.cursor()

            cursor.execute('INSERT INTO "ESTIMATES" ("NAME", "PHONE", "EMAIL", "DATE", "ADDRESS", "CITY", "ZIP_CODE", "HANDLED", "DESCRIPTION") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING "PRIMARY_KEY"',
                                (name, phone, email, date, address, city, zipCode, False, description))

            requestID = cursor.fetchone()[0]
            connect.commit()

            cursor.execute('SELECT * FROM "ESTIMATES" WHERE "PRIMARY_KEY" = %s', (requestID,))
            requestData = cursor.fetchone()

            sendEstimateRequestEmail(requestData)

            return redirect(url_for('home.home'))

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

def sendEstimateRequestEmail(requestData):
    senderEmail = os.getenv("EMAIL_USER")
    senderPassword = os.getenv("EMAIL_PASSWORD")

    subject = f"Estimate Request from {requestData[1]}, ID: {requestData[0]}"

    body = f"""
    A new estimate request has been submitted.<br>
    Request ID: {requestData[0]}<br><br>
    Date: {requestData[4]}<br>
    Name: {requestData[1]}<br>
    Phone: {requestData[2]}<br>
    Email: {requestData[3]}<br>
    Address: {requestData[5]}, {requestData[6]}, {requestData[7]}<br>
    Description: {requestData[9]}
    """

    try:
        connect = connect_to_db()
        cursor = connect.cursor()
        cursor.execute('SELECT "EMPLOYEE_EMAIL" FROM "EMPLOYEE_CREDENTIALS" WHERE "EMAIL_LIST" = TRUE')
        email_rows = cursor.fetchall()
        recipientEmails = [row[0] for row in email_rows]
        recipientEmails.append("denheyerhelper@gmail.com")

        if not recipientEmails:
            print("No recipients subscribed to email list.")
            return

        msg = MIMEMultipart()
        msg['From'] = senderEmail
        msg['To'] = ", ".join(recipientEmails)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(senderEmail, senderPassword)
        server.sendmail(senderEmail, recipientEmails, msg.as_string())
        server.quit()
        print("Email sent successfully")

    except Exception as e:
        print(f"Error sending email: {e}")

    finally:
        if cursor: cursor.close()
        if connect: connect.close()
