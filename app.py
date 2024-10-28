# app.py
from flask import Flask, render_template, redirect, url_for, session
from models import db, User, Service, ServiceRequest
from Folder1.admin_dashboard import admin_blueprint

app = Flask(__name__)
app.config.from_object('config')
db.init_app(app)

# Register blueprints for modular routing
app.register_blueprint(admin_blueprint, url_prefix="/admin")

if __name__ == "__main__":
    app.run(debug=True)
