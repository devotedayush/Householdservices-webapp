from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from models import db, ServiceCategory, ServicePackage, ServiceRequest
from datetime import datetime

customer_view = Blueprint('customer_view', __name__)

@customer_view.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    categories = ServiceCategory.query.all()
    service_requests = ServiceRequest.query.filter_by(customer_id=session['user_id']).all()
    
    return render_template('customer_dashboard.html', 
                         categories=categories,
                         service_requests=service_requests)



@customer_view.route('/summary')
def summary():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    requests = ServiceRequest.query.filter_by(customer_id=session['user_id'])
    total_requests = requests.count()
    ongoing_requests = requests.filter_by(status='requested').count()
    completed_requests = requests.filter_by(status='completed').count()
    cancelled_requests = requests.filter_by(status='cancelled').count()
    
    return render_template('customer_summary.html',
                         total=total_requests,
                         ongoing=ongoing_requests,
                         completed=completed_requests,
                         cancelled=cancelled_requests)

