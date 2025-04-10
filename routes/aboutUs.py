from flask import Blueprint, request, render_template, redirect, url_for, session, jsonify
from databaseModule import connect_to_db

aboutUsBP = Blueprint('aboutUsBP', __name__)

@aboutUsBP.route('/aboutUs')
def aboutUs():
    return "This is the About Us page, this will be filled once DenHeyer provides us with the information they'd like here"