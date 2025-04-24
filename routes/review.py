from flask import Blueprint, request, render_template, jsonify
from databaseModule import connect_to_db  # Import the DB connection function
from app import currentTime

reviewBP = Blueprint('review', __name__)

@reviewBP.route('/reviews', methods=['GET'])
def reviews():
    try:
        # Define the number of reviews per page
        reviews_per_page = 5

        # Get the page number from the URL (default to 1 if not provided)
        page = request.args.get('page', 1, type=int)

        # Calculate the offset for the SQL query
        offset = (page - 1) * reviews_per_page

        # Connect to the database
        connect = connect_to_db()
        cursor = connect.cursor()

        # Execute the query with LIMIT and OFFSET for pagination
        cursor.execute('SELECT "NAME", "DESCRIPTION", "DATE" FROM "REVIEWS" WHERE "PUBLIC" = TRUE LIMIT %s OFFSET %s', (reviews_per_page, offset))
        review_data = cursor.fetchall()

        # Check if there are no reviews
        if not review_data:
            return '''No reviews available.<br>
                      <a href="/writeAReview">Write a review</a>'''

        # Format reviews as templates
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

        # Get the total number of reviews to calculate pagination
        cursor.execute('SELECT COUNT(*) FROM "REVIEWS" WHERE "PUBLIC" = TRUE')
        total_reviews = cursor.fetchone()[0]

        # Calculate the total number of pages
        total_pages = (total_reviews + reviews_per_page - 1) // reviews_per_page

        # Generate pagination links
        pagination_links = ""
        for p in range(1, total_pages + 1):
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
