from flask import Flask
from .extensions import db, migrate, login_manager
from .auth.routes import auth_bp
from .superadmin.routes import superadmin_bp
from .tenant.routes import tenant_bp
from .middleware import load_tenant

def create_app(config_object="config.Config"):
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(config_object)

    # extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(superadmin_bp, url_prefix="")
    app.register_blueprint(tenant_bp, url_prefix="")

    app.before_request(load_tenant)

    return app
