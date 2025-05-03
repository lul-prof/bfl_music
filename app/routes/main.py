from flask import Blueprint, render_template, request, jsonify
from app.models import Service, Order
from app import db

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    services = Service.query.all()
    return render_template('main/index.html', services=services)

@bp.route('/services')
def services():
    services = Service.query.all()
    return render_template('main/services.html', services=services)

@bp.route('/about')
def about():
    return render_template('main/about.html')

@bp.route('/contact')
def contact():
    return render_template('main/contact.html')