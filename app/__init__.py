from flask import Flask
from config import Config
from .extensions import db, migrate, login_manager
from .middleware import load_tenant
from .auth.routes import auth_bp
from .superadmin.routes import superadmin_bp
from .admin.routes import admin_bp

def create_app():
    app = Flask(__name__, template_folder="app/templates", static_folder="app/static")
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

    # Tenant loader before each request
    app.before_request(load_tenant)

    # Import models for migrations context
    with app.app_context():
        from . import models

    return app
