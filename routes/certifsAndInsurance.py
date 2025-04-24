from flask import Blueprint, request, render_template, redirect, url_for, session, jsonify

certifsAndInsuranceBP = Blueprint('certifsAndInsuranceBP', __name__)

@certifsAndInsuranceBP.route('/certifsAndInsurance')
def certifsAndInsurance():
    return render_template('certifsAndInsurance.html')