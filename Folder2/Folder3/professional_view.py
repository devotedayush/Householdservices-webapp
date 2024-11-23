# professional_view/professional_view.py
from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from models import Professional, ServiceRequest, ServicePackage, RejectedServiceRequest, db
from datetime import datetime, timedelta
from sqlalchemy import and_
professional_view = Blueprint('professional_view', __name__)

@professional_view.before_request
def check_professional_login():
    if 'professional_id' not in session:
        print(session)
        return redirect(url_for('auth.login'))

@professional_view.route('/dashboard')
def dashboard():
    professional_id = session.get('professional_id')
    professional = Professional.query.get(professional_id)
    
    if not professional:
        return redirect(url_for('auth.login'))
    
    if professional.status == 'pending':
        return render_template('professional/pending_verification.html')
    elif professional.status == 'rejected':
        return render_template('professional/reject.html')
    
    # Get all service requests that match professional's service package
    # and are either unassigned or assigned to this professional
    service_requests = ServiceRequest.query.join(
        ServicePackage
    ).filter(
        and_(
            ServicePackage.id == professional.service_package_id,
            (ServiceRequest.professional_id.is_(None) |
             ServiceRequest.professional_id == professional_id),
            ServiceRequest.status != 'completed'
        )
    ).all()
    
    # Filter out requests that this professional has already rejected
    rejected_requests = RejectedServiceRequest.query.filter_by(
        professional_id=professional_id
    ).with_entities(RejectedServiceRequest.service_request_id).all()
    rejected_ids = [r[0] for r in rejected_requests]
    
    service_requests = [r for r in service_requests if r.id not in rejected_ids]

    return render_template('professional/dashboard.html',
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
    
    return render_template('professional/summary.html',
                         assigned_count=assigned_count,
                         completed_count=completed_count,
                         rejected_count=rejected_count,
                         completion_rate=completion_rate)

@professional_view.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        request_id = request.form.get('request_id')
        professional_id = session.get('professional_id')
        professional = Professional.query.get(professional_id)
        
        service_request = ServiceRequest.query.filter_by(
            id=request_id,
            service_package_id=professional.service_package_id
        ).first()
        
        if not service_request:
            flash('Service request not found or you do not have access to it.', 'warning')
        
        return render_template('professional/search.html',
                             service_request=service_request)
    
    return render_template('professional/search.html')

