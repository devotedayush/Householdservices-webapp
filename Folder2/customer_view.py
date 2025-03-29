from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from models import db, ServiceCategory, ServicePackage, ServiceRequest, Customer
from datetime import datetime

customer_view = Blueprint('customer_view', __name__)

@customer_view.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('authentication.user_login'))
    
    customer = Customer.query.get(session['user_id'])
    categories = ServiceCategory.query.all()
    service_requests = ServiceRequest.query.filter_by(customer_id=session['user_id']).all()
    
    return render_template('customer_dashboard.html', 
                         customer=customer,
                         categories=categories,
                         service_requests=service_requests)



@customer_view.route('/summary')
def summary():
    if 'user_id' not in session:
        return redirect(url_for('authentication.user_login'))
    
    requests = ServiceRequest.query.filter_by(customer_id=session['user_id'])
    total_requests = requests.count()
    ongoing_requests = requests.filter_by(status='requested').count()
    completed_requests = requests.filter_by(status='completed').count()
    cancelled_requests = requests.filter_by(status='cancelled').count()
    
    # Create data for the chart
    request_status = {
        'requested': ongoing_requests,
        'completed': completed_requests,
        'cancelled': cancelled_requests
    }
    
    return render_template('customer_summary.html',
                         total=total_requests,
                         ongoing=ongoing_requests,
                         completed=completed_requests,
                         cancelled=cancelled_requests,
                         request_status=request_status)


@customer_view.route('/search', methods=['GET'])
def search():
    if 'user_id' not in session:
        return redirect(url_for('authentication.user_login'))
    
    search_query = request.args.get('service_name', '').strip()
    
    # Search for services that contain the search query in their name
    services = ServicePackage.query
    if search_query:
        services = services.filter(ServicePackage.name.ilike(f'%{search_query}%'))
    services = services.all()
    
    categories = ServiceCategory.query.all()
    
    return render_template('customer_search.html',
                         services=services,
                         categories=categories,
                         search_query=search_query)

