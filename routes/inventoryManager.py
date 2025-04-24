from flask import Blueprint, request, render_template, redirect, url_for, session, jsonify
from databaseModule import connect_to_db

inventoryManagerBP = Blueprint('inventoryManager', __name__)

@inventoryManagerBP.route("/addItem", methods=['GET', 'POST'])