from flask import Blueprint, render_template, request, redirect, url_for, flash, g, abort
from flask_login import login_required, current_user
from ..extensions import db
from ..models import User, RoleEnum

tenant_bp = Blueprint("tenant", __name__, template_folder="templates", static_folder="static")

def require_client_admin(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        if current_user.role.name == "SUPER_ADMIN":
            # superadmin has access
            return fn(*args, **kwargs)
        if current_user.tenant_id != getattr(g.tenant, "id", None):
            abort(403)
        if current_user.role.name not in ("CLIENT_ADMIN", "SUPER_ADMIN"):
            abort(403)
        return fn(*args, **kwargs)
    return wrapper

@tenant_bp.route("/tenant/dashboard")
@login_required
@require_client_admin
def dashboard():
    tenant = g.tenant or current_user.tenant
    admins = User.query.filter_by(tenant_id=tenant.id).filter(User.role == RoleEnum.CLIENT_ADMIN).all()
    employees = User.query.filter_by(tenant_id=tenant.id).filter(User.role == RoleEnum.EMPLOYEE).all()
    return render_template("tenant/dashboard.html", tenant=tenant, admins=admins, employees=employees)

@tenant_bp.route("/tenant/create_employee", methods=["GET", "POST"])
@login_required
@require_client_admin
def create_employee():
    tenant = g.tenant or current_user.tenant
    if request.method == "POST":
        email = request.form.get("email")
        full_name = request.form.get("full_name")
        role = request.form.get("role") or "EMPLOYEE"
        # Prevent duplicate email in same tenant
        if User.query.filter_by(email=email, tenant_id=tenant.id).first():
            flash("User already exists for this tenant", "danger")
            return redirect(url_for("tenant.create_employee"))
        u = User(email=email, full_name=full_name, role=RoleEnum[role], tenant_id=tenant.id)
        u.set_password("ChangeMe123!")  # better: send invite + set password flow
        db.session.add(u)
        db.session.commit()
        flash("Employee created", "success")
        return redirect(url_for("tenant.dashboard"))
    return render_template("tenant/create_employee.html")
