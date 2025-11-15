from flask import Blueprint, render_template, request, redirect, url_for, flash, g, current_app
from flask_login import login_user, logout_user, login_required, current_user
from ..extensions import db, login_manager
from ..models import User, RoleEnum
from werkzeug.security import check_password_hash

auth_bp = Blueprint("auth", __name__, template_folder="templates", static_folder="static")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # First, find the user by email (regardless of tenant)
        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash("Invalid credentials", "danger")
            return redirect(url_for("auth.login"))

        # Check if user is active
        if not user.is_active:
            flash("Account is deactivated", "danger")
            return redirect(url_for("auth.login"))

        # For client admins/students, verify they're accessing from correct tenant context
        if user.role != RoleEnum.SUPER_ADMIN:
            # If there's a tenant context, verify the user belongs to this tenant
            if getattr(g, "tenant", None) and user.tenant_id != g.tenant.id:
                flash("Invalid tenant access", "danger")
                return redirect(url_for("auth.login"))
            # If no tenant context (root login), allow login but redirect
            elif not getattr(g, "tenant", None):
                login_user(user)
                flash("Logged in successfully", "success")
                return redirect(url_for("admin.dashboard"))

        # For super admin or valid tenant clients
        login_user(user)
        flash("Logged in successfully", "success")

        # redirect depending on role
        if user.role == RoleEnum.SUPER_ADMIN:
            return redirect(url_for("superadmin.index"))
        else:
            return redirect(url_for("admin.dashboard"))

    return render_template("auth/login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully", "info")
    return redirect(url_for("auth.login"))

# flask-login user loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
