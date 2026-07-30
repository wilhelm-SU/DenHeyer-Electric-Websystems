from flask import Blueprint, jsonify
import requests
import os


googleReviewsBP = Blueprint(
    "googleReviews",
    __name__
)


API_REVIEW_KEY = os.getenv("API_REVIEW_KEY")
API_PLACE_ID = os.getenv("API_PLACE_ID")


def get_google_reviews():

    url = f"https://places.googleapis.com/v1/places/{API_PLACE_ID}"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_REVIEW_KEY,
        "X-Goog-FieldMask": (
            "displayName,"
            "rating,"
            "userRatingCount,"
            "googleMapsUri,"
            "reviews.text,"
            "reviews.rating,"
            "reviews.authorAttribution"
                )
    }

    response = requests.get(
        url,
        headers=headers
    )

    print("Google Status:", response.status_code)
    print("Google Response:", response.text)

    if response.status_code != 200:
        return None

    return response.json()



@googleReviewsBP.route("/googleReviews")
def googleReviews():

    reviews = get_google_reviews()

    if reviews is None:
        return jsonify({
            "error": "Unable to retrieve Google Reviews"
        }), 500

    return jsonify(reviews)