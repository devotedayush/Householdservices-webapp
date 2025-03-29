# professional_view/professional_view.py
from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from models import Professional, ServiceRequest, ServicePackage, RejectedServiceRequest, db, Customer
from datetime import datetime, timedelta
from sqlalchemy import and_
professional_view = Blueprint('professional_view', __name__)

@professional_view.before_request
def check_professional_login():
    if 'professional_id' not in session:
        return redirect(url_for('authentication.user_login'))

@professional_view.route('/dashboard')
def dashboard():
    professional_id = session.get('professional_id')
    professional = Professional.query.get(professional_id)
    
    if not professional:
        return redirect(url_for('authentication.user_login'))
    
    if professional.status == 'pending':
        return render_template('professional/pending_verification.html')
    elif professional.status == 'rejected':
        return render_template('professional/reject.html')
    
    # Get all service requests that match professional's service package
    service_requests = ServiceRequest.query.filter(
        ServiceRequest.service_package_id == professional.service_package_id,
        ServiceRequest.status != 'completed'
    ).all()
    
    # Filter out requests that this professional has already rejected
    rejected_requests = RejectedServiceRequest.query.filter_by(
        professional_id=professional_id
    ).with_entities(RejectedServiceRequest.service_request_id).all()
    rejected_ids = [r[0] for r in rejected_requests]
    
    service_requests = [r for r in service_requests if r.id not in rejected_ids]

    return render_template('professional/dashboard.html',
                         professional=professional,
                         service_requests=service_requests)

@professional_view.route('/summary')
def summary():
    professional_id = session.get('professional_id')
    
    # Get counts of different request statuses
    assigned_count = ServiceRequest.query.filter_by(
        professional_id=professional_id,
        status='assigned'
    ).count()
    
    completed_count = ServiceRequest.query.filter_by(
        professional_id=professional_id,
        status='completed'
    ).count()
    
    rejected_count = RejectedServiceRequest.query.filter_by(
        professional_id=professional_id
    ).count()
    
    # Calculate completion rate
    total_handled = assigned_count + completed_count + rejected_count
    completion_rate = (completed_count / total_handled * 100) if total_handled > 0 else 0
    avg_rating = Professional.query.get(professional_id).get_average_rating()  
    
    return render_template('professional/summary.html',
                         assigned_count=assigned_count,
                         completed_count=completed_count,
                         rejected_count=rejected_count,
                         completion_rate=completion_rate,
                         avg_rating=avg_rating)

@professional_view.route('/search', methods=['GET', 'POST'])
def search():
    professional_id = session.get('professional_id')
    professional = Professional.query.get(professional_id)
    
    if request.method == 'POST':
        search_city = request.form.get('city', '').strip()
        
        # Build the query for the professional's service package
        query = ServiceRequest.query.filter_by(service_package_id=professional.service_package_id)
        
        # Add city filter if provided
        if search_city:
            query = query.join(ServiceRequest.customer).filter(
                db.func.lower(Customer.city).like(f"%{search_city.lower()}%")
            )
        
        service_requests = query.all()
        
        if not service_requests:
            flash('No service requests found in this city for your service category.', 'warning')
        
        return render_template('professional/search.html',
                             service_requests=service_requests,
                             search_city=search_city)
    
    return render_template('professional/search.html')

