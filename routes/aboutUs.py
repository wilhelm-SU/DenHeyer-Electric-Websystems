from flask import Blueprint, request, render_template, redirect, url_for, session, jsonify
from databaseModule import connect_to_db

aboutUsBP = Blueprint('aboutUsBP', __name__)
# About Us page, which can be filled with personal/informative information about the company and its history
@aboutUsBP.route('/aboutUs')
def aboutUs():
    return render_template('aboutUs.html')