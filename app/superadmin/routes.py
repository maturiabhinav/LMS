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
    
    # Get all tenants with additional data
    tenants = Tenant.query.order_by(Tenant.created_at.desc()).all()
    
    # Enhance tenant data with counts and payment info
    enhanced_tenants = []
    for tenant in tenants:
        admin_count = User.query.filter_by(tenant_id=tenant.id, role=RoleEnum.CLIENT_ADMIN).count()
        student_count = Student.query.filter_by(tenant_id=tenant.id).count()
        
        enhanced_tenants.append({
            'id': tenant.id,
            'name': tenant.name,
            'subdomain': tenant.subdomain,
            'created_at': tenant.created_at,
            'admin_count': admin_count,
            'student_count': student_count,
            'amount_paid': 0,  # You can add payment logic later
            'balance_due': 0   # You can add payment logic later
        })
    
    return render_template("super_admin/index.html", 
                         total_clients=total_clients,
                         total_admins=total_admins,
                         total_students=total_students,
                         tenants=enhanced_tenants)

@superadmin_bp.route("/admin/clients", methods=["GET", "POST"])
@login_required
@require_superadmin
def clients():
    if request.method == "POST":
        # Get education center data
        name = request.form.get("name")
        subdomain = request.form.get("subdomain") or slugify(name)
        slug = slugify(name)
        
        # Get admin user data
        admin_name = request.form.get("admin_name")
        admin_email = request.form.get("admin_email")
        admin_password = request.form.get("admin_password")
        confirm_password = request.form.get("confirm_password")
        
        # Validate passwords match
        if admin_password != confirm_password:
            flash("Passwords do not match", "danger")
            return redirect(url_for("superadmin.clients"))
        
        # Check if subdomain already exists
        if Tenant.query.filter_by(subdomain=subdomain).first():
            flash("Subdomain already exists", "danger")
            return redirect(url_for("superadmin.clients"))
            
        # Check if admin email already exists
        if User.query.filter_by(email=admin_email).first():
            flash("Admin email already exists", "danger")
            return redirect(url_for("superadmin.clients"))

        try:
            # Create the education center (tenant)
            tenant = Tenant(name=name, subdomain=subdomain, slug=slug, created_by=current_user.id)
            db.session.add(tenant)
            db.session.flush()  # Get the tenant ID
            
            # Create the admin user for this center
            admin = User(
                email=admin_email,
                full_name=admin_name,
                role=RoleEnum.CLIENT_ADMIN,
                tenant_id=tenant.id
            )
            admin.set_password(admin_password)
            db.session.add(admin)
            
            db.session.commit()
            
            flash(f"Education center '{name}' created successfully with admin '{admin_name}'", "success")
            return redirect(url_for("superadmin.clients"))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating education center: {str(e)}", "danger")
            return redirect(url_for("superadmin.clients"))

    tenants = Tenant.query.order_by(Tenant.created_at.desc()).all()
    return render_template("super_admin/clients.html", tenants=tenants)

@superadmin_bp.route("/admin/clients/<int:tenant_id>")
@login_required
@require_superadmin
def client_detail(tenant_id):
    tenant = Tenant.query.get_or_404(tenant_id)
    admins = User.query.filter_by(tenant_id=tenant.id, role=RoleEnum.CLIENT_ADMIN).all()
    students = Student.query.filter_by(tenant_id=tenant.id).all()
    return render_template("super_admin/client_detail.html",  # FIXED: super_admin
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
        
    return render_template("super_admin/create_admin.html", tenant=tenant) 
