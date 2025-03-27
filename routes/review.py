from flask import Blueprint, request, render_template, jsonify
from databaseModule import connect_to_db  # Import the DB connection function
import pytz
from app import currentTime

reviewBP = Blueprint('review', __name__)

@reviewBP.route('/reviews', methods=['GET'])
def reviews():
    try:
        connect = connect_to_db()
        cursor = connect.cursor()
        cursor.execute('SELECT "NAME", "DESCRIPTION", "DATE" FROM "REVIEWS" WHERE "PUBLIC" = TRUE')

        reviewData = cursor.fetchall()

        if not reviewData:
            return '''No reviews available.<br>
                      <a href="/writeAReview">Write a review</a>'''

        # Format reviews as HTML
        formatted_reviews = "<br><br>".join([
            f"<strong>Name:</strong> {row[0]}<br><strong>Description:</strong> {row[1]} <br><strong>Date:</strong> {row[2]}"
            for row in reviewData
        ])

        return f'''<h2>Welcome to the reviews</h2>
                   {formatted_reviews}
                   <br><br>
                   <a href="/writeAReview">Write a review</a><br>
                   <a href="/">Return</a>''', 200

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

@reviewBP.route('/writeAReview', methods=['GET', 'POST'])
def writeAReview():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        review = request.form.get('review')
        date = currentTime

        if not name or not email or not review:
            return "All fields are required.", 400

        try:
            connect = connect_to_db()
            cursor = connect.cursor()

            cursor.execute('INSERT INTO "REVIEWS" ("NAME", "EMAIL", "DESCRIPTION", "DATE") VALUES (%s, %s, %s, %s)',
                           (name, email, review, date))
            connect.commit()

            return '''
            Thanks for your review!<br>
            <a href="/">Return</a>
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

    # Render the template form from the templates folder
    return render_template('submitReviewForm.html')
