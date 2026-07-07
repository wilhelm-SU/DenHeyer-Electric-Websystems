from flask import Blueprint, request, render_template, jsonify, redirect, url_for, flash
from databaseModule import connect_to_db  # Import the DB connection function
from app import currentTime
from submissionLimit import canSubmit
from dotenv import load_dotenv
import os
import requests

load_dotenv()

RECAPTCHA_SITE_KEY = os.getenv("RECAPTCHA_SITE_KEY")
RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY")

reviewBP = Blueprint('review', __name__)

@reviewBP.route('/reviews', methods=['GET'])
def reviews():
    try:

        reviews_per_page = 5
        page = request.args.get('page', 1, type=int)
        offset = (page - 1) * reviews_per_page

        connect = connect_to_db()
        cursor = connect.cursor()

        cursor.execute('SELECT "NAME", "DESCRIPTION", "DATE" FROM "REVIEWS" WHERE "PUBLIC" = TRUE LIMIT %s OFFSET %s', (reviews_per_page, offset))
        review_data = cursor.fetchall()

        if not review_data:
            return '''No reviews available.<br>
                      <a href="/writeAReview">Write a review</a>'''

        formatted_reviews = ""
        for row in review_data:
            formatted_reviews += f'''
            <div class="review-card">
                <h3>{row[0]}</h3>
                <p><strong>Review:</strong> {row[1]}</p>
                <p><strong>Date:</strong> {row[2]}</p>
            </div>
            <hr>
            '''

        cursor.execute('SELECT COUNT(*) FROM "REVIEWS" WHERE "PUBLIC" = TRUE')

        total_reviews = cursor.fetchone()[0]
        total_pages = (total_reviews + reviews_per_page - 1) // reviews_per_page
        pagination_links = ""
        for p in range(1, total_pages + 1):
            if p == page:
                pagination_links += f"<strong>{p}</strong> "
            else:
                pagination_links += f'<a href="/reviews?page={p}">{p}</a> '

        return render_template('reviews.html', formatted_reviews=formatted_reviews, pagination_links=pagination_links)

    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred while fetching reviews. Please try again later.", 500
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

        # Google reCAPTCHA verification
        recaptcha_response = request.form.get("g-recaptcha-response")

        verification = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={
                "secret": RECAPTCHA_SECRET_KEY,
                "response": recaptcha_response
            }
        )

        result = verification.json()

        if not result.get("success"):
            flash("Please complete the reCAPTCHA verification.", "warning")
            return redirect(url_for('review.writeAReview'))

        if not canSubmit(1):
            flash(f"You can only submit {1} review.", "warning")
            return redirect(url_for('review.writeAReview'))

        name = request.form.get('name')
        email = request.form.get('email')
        review = request.form.get('review')
        date = currentTime

        if not name or not email or not review:
            return "All fields are required.", 400

        connect = None
        cursor = None

        try:
            connect = connect_to_db()
            cursor = connect.cursor()

            cursor.execute(
                '''
                INSERT INTO "REVIEWS"
                ("NAME", "EMAIL", "DESCRIPTION", "DATE")
                VALUES (%s, %s, %s, %s)
                ''',
                (name, email, review, date)
            )

            connect.commit()

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

    return render_template(
        'submitReviewForm.html',
        recaptcha_site_key=RECAPTCHA_SITE_KEY
    )
