# Household Services Platform

## Overview

This project is a web-based platform for managing household services, connecting customers with service professionals (such as plumbers, cleaners, electricians, etc.) and providing an admin interface for overall management. The application is built using Flask, SQLAlchemy, and Bootstrap, and supports three main user roles:

- **Customer:** Can register, log in, request services, view and manage their requests, and rate professionals.
- **Professional:** Can register, upload documents for verification, accept or reject service requests, and view their performance summary.
- **Admin:** Can manage services, professionals, and requests, approve/reject professionals, and monitor delayed or problematic requests.

The platform features:
- User authentication and role-based dashboards
- Service and category management
- Request assignment and tracking
- Professional document verification
- Summary and analytics dashboards for admin and users

## Project Structure

- `app.py`: Main Flask application and blueprint registration
- `models.py`: SQLAlchemy models for all entities
- `config.py`: Configuration and environment variable loading
- `Folder1/`: Admin and authentication blueprints
- `Folder2/`: Customer and professional blueprints
- `templates/`: Jinja2 HTML templates for all pages
- `static/`: CSS, JS, and uploads
- `instance/database.sqlite3`: SQLite database
- `log.md`: Development log and troubleshooting notes

## Learning and Errors Faced

A detailed log of the learning process and errors encountered during development is maintained in [log.md](log.md). Some key points include:

### 1. Circular Import Error
- **Issue:** Importing `app` in `models.py` before `app.py` is initialized caused circular import errors.
- **Resolution:** Ensured proper import order and initialization sequence.

### 2. Authentication and Routing Issues
- **404 on Login Page:** Checked blueprint registration, route methods, and form actions.
- **Redirect Loops:** Ensured login logic renders templates instead of redirecting unnecessarily.
- **URL Building Errors:** Verified that Jinja `url_for` references valid endpoints.

### 3. Admin Dashboard Problems
- **Blueprint Registration:** Confirmed `admin_dashboard.py` blueprint is registered in `app.py`.
- **Route Naming:** Ensured route names and URLs match between templates and blueprints.

### 4. Service Management Errors
- **Integrity Errors:** Checked form value retrieval and database commit logic.
- **Method Not Allowed:** Ensured destructive actions (like delete) use POST, not GET.
- **Key Errors:** Created missing directories/files as needed.

### 5. Customer and Professional Dashboards
- **Customer:** Built dashboard to show service categories, requests, and summary.
- **Professional:** Managed dashboard logic for pending/approved/rejected status, request assignment, and rejection tracking.

### 6. Blueprint Import Errors
- **Solution:** Registered all blueprints in `app.py` and used correct naming conventions.

### 7. Static File Issues
- **404 on CSS/JS:** Ensured static files exist and are referenced correctly in templates.

### 8. Session and Role Management
- **Professional Login:** Fixed session keys to distinguish between `user_id` and `professional_id`.

### 9. Search and Summary Features
- Implemented search for services and requests for all user roles.
- Added summary and analytics sections using Chart.js.

### 10. Admin Alerts and Delayed Requests
- Added admin alerts for delayed requests and professional verification.

### 11. Customer Request Completion
- Implemented logic for customers to close requests with ratings and remarks.

### 12. SQLAlchemy Relationship Definitions
- Clarified relationship definitions to avoid redundancy and ensure correct ORM behavior.

For more detailed explanations and troubleshooting steps, see [log.md](log.md).

---

## Setup Instructions

1. Clone the repository.
2. Install dependencies from `requirements.txt`.
3. Set up the `.env` file with your configuration.
4. Run the application with `python app.py`.

---

## License

This project is for educational purposes.
