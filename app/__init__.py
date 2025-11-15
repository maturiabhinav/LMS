from flask import Flask, redirect, url_for, jsonify
import os
from config import Config
from .extensions import db, migrate, login_manager
from .middleware import load_tenant
from .auth.routes import auth_bp
from .superadmin.routes import superadmin_bp
from .admin.routes import admin_bp

def create_app():
    # Get the directory where this __init__.py file is located
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    app = Flask(__name__, 
                template_folder=os.path.join(base_dir, 'templates'), 
                static_folder=os.path.join(base_dir, 'static'))
    
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
    
    @app.route('/debug-db-info')
    def debug_db_info():
        import os
        from sqlalchemy import text
    
        info = {
            'database_url': os.getenv('DATABASE_URL'),
            'sqlalchemy_database_uri': current_app.config.get('SQLALCHEMY_DATABASE_URI'),
            'database_driver': current_app.extensions['sqlalchemy'].db.engine.driver
        }
    
        try:
            # Try to get database version
            result = db.session.execute(text("SELECT version()"))
            db_version = result.scalar()
            info['database_version'] = db_version
            info['database_type'] = 'PostgreSQL'
        except Exception as e:
            info['database_error'] = str(e)
            info['database_type'] = 'Unknown'
    
        return jsonify(info)
    

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
    
    @app.route('/debug-template-paths')
    def debug_template_paths():
        import os
        from flask import current_app
    
        # Get all possible template paths
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        template_dir_from_init = os.path.join(current_file_dir, 'templates')
    
        info = {
            'current_file': __file__,
            'current_file_directory': current_file_dir,
            'flask_template_folder': current_app.template_folder,
            'flask_template_folder_absolute': os.path.abspath(current_app.template_folder),
            'calculated_template_dir': template_dir_from_init,
        
            # Check specific template paths
            'client_detail_relative_path': 'super_admin/client_detail.html',
            'client_detail_absolute_path_flask': os.path.join(current_app.template_folder, 'super_admin', 'client_detail.html'),
            'client_detail_absolute_path_calculated': os.path.join(template_dir_from_init, 'super_admin', 'client_detail.html'),
        
            # Check if paths exist
            'flask_template_folder_exists': os.path.exists(current_app.template_folder),
            'calculated_template_dir_exists': os.path.exists(template_dir_from_init),
            'client_detail_exists_flask': os.path.exists(os.path.join(current_app.template_folder, 'super_admin', 'client_detail.html')),
            'client_detail_exists_calculated': os.path.exists(os.path.join(template_dir_from_init, 'super_admin', 'client_detail.html')),
        }
    
        # List contents if directories exist
        if os.path.exists(current_app.template_folder):
            info['flask_template_contents'] = os.listdir(current_app.template_folder)
            if os.path.exists(os.path.join(current_app.template_folder, 'super_admin')):
                info['super_admin_contents_flask'] = os.listdir(os.path.join(current_app.template_folder, 'super_admin'))
    
        if os.path.exists(template_dir_from_init):
            info['calculated_template_contents'] = os.listdir(template_dir_from_init)
            if os.path.exists(os.path.join(template_dir_from_init, 'super_admin')):
                info['super_admin_contents_calculated'] = os.listdir(os.path.join(template_dir_from_init, 'super_admin'))
    
        return jsonify(info)

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