
from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from models import db, ServiceCategory, ServicePackage, ServiceRequest
from datetime import datetime
customer_services = Blueprint('customer_services', __name__)

@customer_services.route('/request_service/<int:package_id>', methods=['POST'])
def request_service(package_id):
    if 'user_id' not in session:
        return redirect(url_for('authentication.user_login'))
    
    service_request = ServiceRequest(
        customer_id=session['user_id'],
        service_package_id=package_id,
        date_of_request=datetime.now(),
        status="requested"
    )

    db.session.add(service_request)
    db.session.commit()
    flash('Service requested successfully!', 'success')
    return redirect(url_for('customer_view.dashboard'))

@customer_services.route('/complete_request/<int:request_id>', methods=['GET', 'POST'])
def complete_request(request_id):
    if request.method == 'POST':
        remarks = request.form.get('remarks')
        rating = request.form.get('rating')
        
        service_request = ServiceRequest.query.get_or_404(request_id)
        service_request.status = "completed"
        service_request.remarks = remarks
        service_request.rating = rating
        service_request.date_of_completion = datetime.now()
        
        db.session.commit()
        flash('Service marked as completed!', 'success')
        return redirect(url_for('customer_view.dashboard'))
    
    return render_template('remark.html', request_id=request_id)

@customer_services.route('/cancel_request/<int:request_id>', methods=['POST'])
def cancel_request(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)
    db.session.delete(service_request)
    db.session.commit()
    flash('Service request cancelled!', 'success')
    return redirect(url_for('customer_view.dashboard'))


    
    # things it's carrying in cache , also on that page redirection. 
        # when a customer logs in, the authentication.user_login stores the user_id and role in session. 
        # when a customer clicks on complete, the remark.html is rendered
          # the request_id is passed to the remark.html, through which it queries the database object. 
        # when a customer submits the form, the remark.html is posted. 
            # the remarks and rating are stored in the database. 
            # the service request is marked as completed. 
            # the customer is redirected to the dashboard. 
@customer_services.route('/professional_details/<int:request_id>', methods=['GET'])
def professional_details(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)
    return render_template('professional_details.html', service_request=service_request)
