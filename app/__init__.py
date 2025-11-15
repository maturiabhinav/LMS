from flask import Flask, redirect, url_for, jsonify
import os
from config import Config
from .extensions import db, migrate, login_manager
from .middleware import load_tenant
from .auth.routes import auth_bp
from .superadmin.routes import superadmin_bp
from .admin.routes import admin_bp

def create_app():
    # Get the base directory of the project
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    app = Flask(__name__, 
                template_folder=os.path.join(base_dir, 'app', 'templates'), 
                static_folder=os.path.join(base_dir, 'app', 'static'))
    
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(superadmin_bp, url_prefix="")
    app.register_blueprint(admin_bp, url_prefix="")

    # Add debug route to check template paths
    @app.route('/debug-templates')
    def debug_templates():
        paths = {
            "current_directory": os.getcwd(),
            "app_directory": os.path.dirname(__file__),
            "base_directory": base_dir,
            "template_folder": app.template_folder,
            "template_folder_exists": os.path.exists(app.template_folder),
            "login_template_path": os.path.join(app.template_folder, 'auth', 'login.html'),
            "login_template_exists": os.path.exists(os.path.join(app.template_folder, 'auth', 'login.html')),
            "template_folder_contents": os.listdir(app.template_folder) if os.path.exists(app.template_folder) else "Template folder not found"
        }
        return jsonify(paths)
    
    @app.route('/debug-users')
    def debug_users():
        from .models import User, Tenant
        import json
    
        users = User.query.all()
        tenants = Tenant.query.all()
    
        user_data = []
        for user in users:
            user_data.append({
                'id': user.id,
                'email': user.email,
                'role': user.role.value,
                'tenant_id': user.tenant_id,
                'has_password': bool(user.password_hash),
                'is_active': user.is_active
            })
    
        tenant_data = []
        for tenant in tenants:
            tenant_data.append({
                'id': tenant.id,
                'name': tenant.name,
                'subdomain': tenant.subdomain
            })
    
        return jsonify({
            'users': user_data,
            'tenants': tenant_data
        })
    
    
    # Add test route
    @app.route('/test')
    def test():
        return jsonify({"status": "success", "message": "App is working!"})

    # Add root route
    @app.route('/')
    def home():
        return redirect(url_for('auth.login'))

    # Tenant loader before each request
    app.before_request(load_tenant)

    # Import models for migrations context
    with app.app_context():
        from . import models

    return app