from flask import Blueprint, request, redirect, url_for, session, render_template, flash, current_app as current_app_instance
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, Customer, Professional, ServicePackage
from werkzeug.utils import secure_filename
import os


authentication_bp = Blueprint('authentication', __name__)

@authentication_bp.route('/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        user_email = request.form.get('email')
        user_password = request.form.get('password')

        # Validate admin user
        admin_user = Customer.query.filter_by(email=user_email, is_admin=True).first()
        if admin_user and admin_user.check_password(user_password):
            session['user_id'] = admin_user.id
            session['role'] = 'admin'
            flash('Successfully logged in!', 'success')
            return redirect(url_for('admin.dashboard'))

        # Validate regular customer
        regular_customer = Customer.query.filter_by(email=user_email, is_admin=False).first()
        if regular_customer and regular_customer.check_password(user_password):
            session['user_id'] = regular_customer.id
            session['role'] = 'customer'
            flash('Successfully logged in!', 'success')
            return redirect(url_for('customer_view.dashboard'))

        # Validate professional user
        professional_user = Professional.query.filter_by(email=user_email).first()
        if professional_user and check_password_hash(professional_user.passhash, user_password):
            session['professional_id'] = professional_user.id
            session['user_id'] = professional_user.id
            session['role'] = 'professional'
            flash('Successfully logged in!', 'success')
            return redirect(url_for('professional_view.dashboard'))

        # Authentication failed
        flash('Incorrect email or password.', 'danger')
        return render_template('login.html')
    return render_template('login.html')

@authentication_bp.route('/register', methods=['GET', 'POST'])
def user_register():
    if request.method == 'POST':
        user_email = request.form.get('email')
        user_password = request.form.get('password')
        full_name = request.form.get('full_name')
        phone = request.form.get('phone_number')
        user_address = request.form.get('address')
        user_city = request.form.get('city')
        user_pincode = request.form.get('pincode')

        # Add address validation
        if not user_address:
            flash('Address is required.', 'danger')
            return redirect(url_for('authentication.user_register'))

        if Customer.query.filter_by(email=user_email).first():
            flash('Email is already in use.', 'danger')
            return redirect(url_for('authentication.user_register'))
        if Customer.query.filter_by(phone_number=phone).first():
            flash('Phone number is already linked to another account.', 'danger')
            return redirect(url_for('authentication.user_register'))

        new_customer = Customer(
            email=user_email,
            passhash=generate_password_hash(user_password),
            full_name=full_name,
            phone_number=phone,
            address=user_address,
            city=user_city,
            pincode=user_pincode,
            is_admin=False
        )
        db.session.add(new_customer)
        db.session.commit()
        return redirect(url_for('authentication.user_login'))
    return render_template('register.html')

@authentication_bp.route('/register/professional', methods=['GET', 'POST'])
def professional_register():
    available_services = ServicePackage.query.all()
    if request.method == 'POST':
        prof_email = request.form.get('email')
        prof_password = request.form.get('password')
        prof_full_name = request.form.get('full_name')
        prof_phone = request.form.get('phone_number')
        prof_city = request.form.get('city')
        prof_pincode = request.form.get('pincode')
        service_package = request.form.get('service_package_id')
        prof_experience = request.form.get('experience')

        if Professional.query.filter_by(email=prof_email).first():
            flash('Email is already registered.', 'danger')
            return redirect(url_for('authentication.professional_register'))
        if Professional.query.filter_by(phone_number=prof_phone).first():
            flash('Phone number is already associated with another account.', 'danger')
            return redirect(url_for('authentication.professional_register'))

        document_path = None

        if 'document' in request.files:
            document = request.files['document']
            if document.filename and is_allowed_file(document.filename):
                secure_name = secure_filename(document.filename)
                document_path = os.path.join(current_app_instance.config['UPLOAD_FOLDER'], secure_name)
                document.save(document_path)
            else:
                flash('Invalid file type. Allowed types: pdf, jpg, jpeg, png.', 'danger')
                return redirect(request.url)
        else:
            flash('Document upload is mandatory.', 'danger')
            return redirect(request.url)

        new_professional = Professional(
            email=prof_email,
            passhash=generate_password_hash(prof_password),
            full_name=prof_full_name,
            phone_number=prof_phone,
            city=prof_city,
            pincode=prof_pincode,
            service_package_id=service_package,
            experience=prof_experience,
            document=document_path
        )
        db.session.add(new_professional)
        db.session.commit()
        flash('Registration completed successfully!', 'success')
        return redirect(url_for('authentication.user_login'))
    return render_template('register_professional.html', services=available_services)

def is_allowed_file(filename):
    permitted_extensions = {'pdf', 'jpg', 'jpeg', 'png'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in permitted_extensions

@authentication_bp.route('/logout')
def user_logout():
    session.clear()
    return redirect(url_for('authentication.user_login'))