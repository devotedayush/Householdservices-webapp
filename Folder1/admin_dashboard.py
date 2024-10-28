# admin_dashboard.py
from flask import Blueprint, render_template, redirect, url_for, session
from models import db, User, Service, ServiceRequest

admin_blueprint = Blueprint('admin', __name__)


@admin_blueprint.route('/dashboard')
def dashboard():
    # Verify if the logged-in user is admin
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    # Fetch data for admin view
    services = Service.query.all()
    professionals = User.query.filter_by(role='professional').all()
    customers = User.query.filter_by(role='customer').all()
    return render_template('admin_dashboard.html', services=services, professionals=professionals, customers=customers)
