from flask import Blueprint, render_template, request, redirect, url_for, flash, g, current_app
from flask_login import login_user, logout_user, login_required, current_user
from ..extensions import db, login_manager
from ..models import User, RoleEnum
from werkzeug.security import check_password_hash

auth_bp = Blueprint("auth", __name__, template_folder="templates", static_folder="static")

@auth_bp.route("/login", methods=["GET", "POST"])  # Remove "/auth" prefix here
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # If tenant context, restrict search to tenant users (client admins / students)
        if getattr(g, "tenant", None):
            user = User.query.filter_by(email=email, tenant_id=g.tenant.id).first()
        else:
            # root context: allow SUPER_ADMIN login (tenant_id NULL)
            user = User.query.filter_by(email=email, tenant_id=None).first()

        if not user or not user.check_password(password):
            flash("Invalid credentials", "danger")
            return redirect(url_for("auth.login"))

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
