from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, g
from flask_login import login_user, logout_user, login_required, current_user
from ..extensions import db, login_manager
from ..models import User, RoleEnum, Tenant
from werkzeug.security import generate_password_hash

auth_bp = Blueprint("auth", __name__, template_folder="templates", static_folder="static")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Login endpoint. It determines if we are in tenant context (g.tenant) or superadmin context.
    """
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        # If tenant context, restrict search to tenant users (except superadmin)
        if getattr(g, "tenant", None):
            user = User.query.filter_by(email=email, tenant_id=g.tenant.id).first()
        else:
            user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Invalid credentials", "danger")
            return redirect(url_for("auth.login"))
        login_user(user)
        flash("Logged in", "success")
        # Redirect logic: superadmin -> superadmin dashboard; client admin -> tenant dashboard
        if user.role.name == "SUPER_ADMIN":
            return redirect(url_for("superadmin.index"))
        else:
            # redirect to tenant dashboard; ensure we have tenant context
            tenant = g.tenant if g.tenant else user.tenant
            if tenant:
                target = f"http://{tenant.subdomain}.{current_app.config.get('SERVER_NAME') or request.host.split(':')[0]}"
                # Prefer an internal route
                return redirect(url_for("tenant.dashboard"))
            else:
                return redirect(url_for("auth.login"))
    return render_template("auth/login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out", "info")
    return redirect(url_for("auth.login"))

# User loader for flask-login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
