from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, current_app
from flask_login import login_required, current_user
from ..extensions import db
from ..models import Tenant, User, RoleEnum, Student
from slugify import slugify

superadmin_bp = Blueprint("superadmin", __name__, template_folder="templates", static_folder="static")

def require_superadmin(fn):
    from functools import wraps
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != RoleEnum.SUPER_ADMIN:
            abort(403)
        return fn(*args, **kwargs)
    return wrapped

@superadmin_bp.route("/admin")
@login_required
@require_superadmin
def index():
    total_clients = Tenant.query.count()
    total_admins = User.query.filter_by(role=RoleEnum.CLIENT_ADMIN).count()
    total_students = Student.query.count()
    return render_template("superadmin/index.html", 
                         total_clients=total_clients,
                         total_admins=total_admins,
                         total_students=total_students)

@superadmin_bp.route("/admin/clients", methods=["GET", "POST"])
@login_required
@require_superadmin
def clients():
    if request.method == "POST":
        name = request.form.get("name")
        subdomain = request.form.get("subdomain") or slugify(name)
        slug = slugify(name)
        
        # ensure unique
        if Tenant.query.filter_by(subdomain=subdomain).first():
            flash("Subdomain already exists", "danger")
            return redirect(url_for("superadmin.clients"))

        tenant = Tenant(name=name, subdomain=subdomain, slug=slug, created_by=current_user.id)
        db.session.add(tenant)
        db.session.commit()
        flash(f"Education center '{name}' created with subdomain: {subdomain}", "success")
        return redirect(url_for("superadmin.clients"))

    tenants = Tenant.query.order_by(Tenant.created_at.desc()).all()
    return render_template("superadmin/clients.html", tenants=tenants)

@superadmin_bp.route("/admin/clients/<int:tenant_id>")
@login_required
@require_superadmin
def client_detail(tenant_id):
    tenant = Tenant.query.get_or_404(tenant_id)
    admins = User.query.filter_by(tenant_id=tenant.id, role=RoleEnum.CLIENT_ADMIN).all()
    students = Student.query.filter_by(tenant_id=tenant.id).all()
    return render_template("superadmin/client_detail.html", 
                         tenant=tenant, 
                         admins=admins, 
                         students=students)

@superadmin_bp.route("/admin/clients/<int:tenant_id>/create-admin", methods=["GET", "POST"])
@login_required
@require_superadmin
def create_client_admin(tenant_id):
    tenant = Tenant.query.get_or_404(tenant_id)
    if request.method == "POST":
        email = request.form.get("email")
        full_name = request.form.get("full_name")
        password = request.form.get("password")
        
        if User.query.filter_by(email=email).first():
            flash("User with this email already exists", "danger")
            return redirect(url_for("superadmin.create_client_admin", tenant_id=tenant_id))
            
        admin = User(
            email=email,
            full_name=full_name,
            role=RoleEnum.CLIENT_ADMIN,
            tenant_id=tenant.id
        )
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        flash(f"Admin '{full_name}' created successfully for {tenant.name}", "success")
        return redirect(url_for("superadmin.client_detail", tenant_id=tenant_id))
        
    return render_template("superadmin/create_admin.html", tenant=tenant)
