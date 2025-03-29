# admin_dashboard.py
from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from models import ServiceRequest, Professional, ServiceCategory, db, Customer, ServicePackage, DelayedRequest
from functools import wraps
from flask import send_file
from datetime import timedelta
from datetime import datetime

admin_blueprint = Blueprint('admin', __name__)

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Please login as admin to access this page.', 'danger')
            return redirect(url_for('authentication.user_login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_blueprint.route('/dashboard')
@admin_required
def dashboard():
    # Fetch all required data with joined loads to optimize queries
    service_requests = ServiceRequest.query.join(Customer).join(ServicePackage).all()
    professionals = Professional.query.all()
    service_packages = ServicePackage.query.all()
    service_categories = ServiceCategory.query.all()
    
    # Get summary counts
    pending_professionals = Professional.query.filter_by(status='pending').count()
    total_services = ServicePackage.query.count()
    active_requests = ServiceRequest.query.filter_by(status='requested').count()
    
    # Identify delayed requests
    fifteen_days_ago = datetime.utcnow() - timedelta(days=15)
    delayed_requests = ServiceRequest.query.filter(
        ServiceRequest.status == 'requested',
        ServiceRequest.date_of_request <= fifteen_days_ago
    ).all()

    # Store delayed requests in the DelayedRequest table
    for request in delayed_requests:
        if not DelayedRequest.query.filter_by(service_request_id=request.id).first():
            delayed_request = DelayedRequest(service_request_id=request.id)
            db.session.add(delayed_request)
    db.session.commit()

    # Fetch delayed requests for display
    delayed_requests = DelayedRequest.query.all()

    return render_template('admin_dashboard.html',
                         professionals=professionals,
                         service_packages=service_packages,
                         service_requests=service_requests,
                         service_categories=service_categories,
                         pending_professionals=pending_professionals,
                         total_services=total_services,
                         active_requests=active_requests,
                         delayed_requests=delayed_requests)
@admin_blueprint.route('/view_document/<int:professional_id>', methods=['GET'])
def view_document(professional_id):
    professional = Professional.query.get_or_404(professional_id)
    if not professional.document:
        flash('No document uploaded for this professional', 'danger')
        return redirect(url_for('admin.dashboard'))

    # Safely return the document file
    return send_file(professional.document, as_attachment=False)


@admin_blueprint.route('/add_category', methods=['POST'])
@admin_required
def add_category():
    name = request.form.get('name')
    category = ServiceCategory(name=name)
    db.session.add(category)
    db.session.commit()
    flash('Category added successfully', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_blueprint.route('/service/add', methods=['POST'])
@admin_required
def add_service():
    name = request.form.get('name')
    price = float(request.form.get('price'))
    time = int(request.form.get('time'))
    description = request.form.get('description')
    service_category_id = request.form.get('service_category_id')
    service = ServicePackage(name=name, price=price, time=time, description=description, service_category_id=service_category_id)
    db.session.add(service)
    db.session.commit()
    flash('Service added successfully', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_blueprint.route('/professional/<int:id>/approve', methods=['POST'])
@admin_required
def approve_professional(id):
    professional = Professional.query.get_or_404(id)
    professional.status = 'approved'
    db.session.commit()
    flash('Professional approved successfully', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_blueprint.route('/professional/<int:id>/reject', methods=['POST'])
@admin_required
def reject_professional(id):
    professional = Professional.query.get_or_404(id)
    professional.status = 'rejected'
    db.session.commit()
    flash('Professional rejected successfully', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_blueprint.route('/professional/<int:id>/delete', methods=['POST'])
@admin_required
def delete_professional(id):
    try:
        professional = Professional.query.get_or_404(id)
        db.session.delete(professional)
        db.session.commit()
        flash('Professional successfully deleted', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Unable to delete professional. They may have associated service requests.', 'danger')
    return redirect(url_for('admin.dashboard'))

@admin_blueprint.route('/service/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_service(id):
    service = ServicePackage.query.get_or_404(id)
    if request.method == 'POST':
        service.name = request.form.get('name')
        service.price = float(request.form.get('price'))
        service.time = int(request.form.get('time'))
        service.description = request.form.get('description')
        db.session.commit()
        flash('Service updated successfully', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('edit_service.html', service=service)

@admin_blueprint.route('/service/<int:id>/delete', methods=['POST'])
@admin_required
def delete_service(id):
    try:
        service = ServicePackage.query.get_or_404(id)
        db.session.delete(service)
        db.session.commit()
        flash('Service deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Unable to delete service. It may have associated service requests.', 'danger')
    return redirect(url_for('admin.dashboard'))

@admin_blueprint.route('/summary')
@admin_required
def summary():
    # Basic counts
    pending_professionals = Professional.query.filter_by(status='pending').count()
    total_services = ServicePackage.query.count()
    active_requests = ServiceRequest.query.filter_by(status='requested').count()
    
    # Professional status distribution
    professional_status = {
        'pending': Professional.query.filter_by(status='pending').count(),
        'approved': Professional.query.filter_by(status='approved').count(),
        'rejected': Professional.query.filter_by(status='rejected').count()
    }
    
    # Service request status distribution
    request_status = {
        'requested': ServiceRequest.query.filter_by(status='requested').count(),
        'assigned': ServiceRequest.query.filter_by(status='assigned').count(),
        'completed': ServiceRequest.query.filter_by(status='completed').count()
    }
    
    return render_template('summary.html',
                         pending_professionals=pending_professionals,
                         total_services=total_services,
                         active_requests=active_requests,
                         professional_status=professional_status,
                         request_status=request_status)

@admin_blueprint.route('/search', methods=['GET'])
@admin_required
def search():
    service_category_id = request.args.get('service_category')
    professional_status = request.args.get('professional_status')
    request_status = request.args.get('request_status')

    # Filter services by category
    services = ServicePackage.query
    if service_category_id:
        services = services.filter_by(service_category_id=service_category_id)
    services = services.all()

    # Filter professionals by status
    professionals = Professional.query
    if professional_status:
        professionals = professionals.filter_by(status=professional_status)
    professionals = professionals.all()

    # Filter service requests by status
    service_requests = ServiceRequest.query
    if request_status:
        service_requests = service_requests.filter_by(status=request_status)
    service_requests = service_requests.all()

    service_categories = ServiceCategory.query.all()

    return render_template('admin_search.html',
                           services=services,
                           professionals=professionals,
                           service_requests=service_requests,
                           service_categories=service_categories)