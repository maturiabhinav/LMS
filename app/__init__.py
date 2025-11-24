from flask import Flask, redirect, url_for, jsonify, current_app
import os
from config import Config
from app.extensions import db, migrate, login_manager
from app.middleware import load_tenant
from app.auth.routes import auth_bp
from app.superadmin.routes import superadmin_bp
from app.admin.routes import admin_bp

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


    # DEBUG ROUTES

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
    
        users = User.query.all()
        tenants = Tenant.query.all()
    
        user_data = [{
            'id': user.id,
            'email': user.email,
            'role': user.role.value,
            'tenant_id': user.tenant_id,
            'has_password': bool(user.password_hash),
            'is_active': user.is_active
        } for user in users]
    
        tenant_data = [{
            'id': tenant.id,
            'name': tenant.name,
            'subdomain': tenant.subdomain
        } for tenant in tenants]
    
        return jsonify({
            'users': user_data,
            'tenants': tenant_data
        })

    @app.route('/debug-db')
    def debug_db():
        from .models import User, Tenant
        from sqlalchemy import inspect
        
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        return {
            'tables': tables,
            'database_url': app.config['SQLALCHEMY_DATABASE_URI'],
            'has_users_table': 'users' in tables,
            'has_tenants_table': 'tenants' in tables
        }

    @app.route('/create-superadmin')
    def create_superadmin():
        from .models import User, RoleEnum
        from .extensions import db
        import os
        
        email = os.getenv("SUPERADMIN_EMAIL")
        password = os.getenv("SUPERADMIN_PASSWORD")
        
        if not email or not password:
            return "SUPERADMIN_EMAIL and SUPERADMIN_PASSWORD environment variables not set"
        
        # Check if super admin already exists
        existing = User.query.filter_by(email=email, role=RoleEnum.SUPER_ADMIN).first()
        if existing:
            return f"Super admin already exists: {email}"
        
        # Create super admin
        admin = User(email=email, full_name="Super Admin", role=RoleEnum.SUPER_ADMIN)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        
        return f"Super admin created successfully: {email}"
        
    @app.route('/debug-template-paths')
    def debug_template_paths():
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        template_dir_from_init = os.path.join(current_file_dir, 'templates')
    
        info = {
            'current_file': __file__,
            'current_file_directory': current_file_dir,
            'flask_template_folder': current_app.template_folder,
            'flask_template_folder_absolute': os.path.abspath(current_app.template_folder),
            'calculated_template_dir': template_dir_from_init,
            'client_detail_relative_path': 'super_admin/client_detail.html',
            'client_detail_absolute_path_flask': os.path.join(current_app.template_folder, 'super_admin', 'client_detail.html'),
            'client_detail_absolute_path_calculated': os.path.join(template_dir_from_init, 'super_admin', 'client_detail.html'),
            'flask_template_folder_exists': os.path.exists(current_app.template_folder),
            'calculated_template_dir_exists': os.path.exists(template_dir_from_init),
            'client_detail_exists_flask': os.path.exists(os.path.join(current_app.template_folder, 'super_admin', 'client_detail.html')),
            'client_detail_exists_calculated': os.path.exists(os.path.join(template_dir_from_init, 'super_admin', 'client_detail.html')),
        }
    
        if os.path.exists(current_app.template_folder):
            info['flask_template_contents'] = os.listdir(current_app.template_folder)
            sa_path = os.path.join(current_app.template_folder, 'super_admin')
            if os.path.exists(sa_path):
                info['super_admin_contents_flask'] = os.listdir(sa_path)
    
        if os.path.exists(template_dir_from_init):
            info['calculated_template_contents'] = os.listdir(template_dir_from_init)
            sa2_path = os.path.join(template_dir_from_init, 'super_admin')
            if os.path.exists(sa2_path):
                info['super_admin_contents_calculated'] = os.listdir(sa2_path)
    
        return jsonify(info)

    @app.route('/test')
    def test():
        return jsonify({"status": "success", "message": "App is working!"})

    @app.route('/')
    def home():
        return redirect(url_for('auth.login'))

    # Tenant loader before each request
    app.before_request(load_tenant)

    # Import models for migrations context
    with app.app_context():
        try:
            db.create_all()
            print("Database tables checked/created")
            
            # Auto-create super admin if not exists
            from .models import User, RoleEnum
            import os
            
            email = os.getenv("SUPERADMIN_EMAIL")
            password = os.getenv("SUPERADMIN_PASSWORD")
            
            if email and password:
                existing = User.query.filter_by(email=email, role=RoleEnum.SUPER_ADMIN).first()
                if not existing:
                    admin = User(email=email, full_name="Super Admin", role=RoleEnum.SUPER_ADMIN)
                    admin.set_password(password)
                    db.session.add(admin)
                    db.session.commit()
                    print(f"Super admin created: {email}")
                else:
                    print(f"Super admin already exists: {email}")
                    
        except Exception as e:
            print(f"Database initialization: {e}")

    with app.app_context():
        from . import models

    return app
