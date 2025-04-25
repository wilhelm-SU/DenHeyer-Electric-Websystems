from flask import Blueprint, request, render_template, redirect, url_for, session, jsonify
from databaseModule import connect_to_db

FAQBP = Blueprint('FAQ', __name__)
# About Us page, which can be filled with personal/informative information about the company and its history
@FAQBP.route('/FAQ')
def FAQ():
    return render_template('FAQ.html')