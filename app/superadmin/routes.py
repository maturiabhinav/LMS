from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, current_app
from flask_login import login_required, current_user
from ..extensions import db
from ..models import Tenant, User, RoleEnum
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
    return render_template("superadmin/index.html")

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
        flash("Client created: " + subdomain, "success")
        return redirect(url_for("superadmin.clients"))

    tenants = Tenant.query.order_by(Tenant.created_at.desc()).all()
    return render_template("superadmin/clients.html", tenants=tenants)


@superadmin_bp.route("/admin/clients/<int:tenant_id>/users")
@login_required
@require_superadmin
def client_users(tenant_id):
    tenant = Tenant.query.get_or_404(tenant_id)
    users = tenant.users.all()
    return render_template("superadmin/clients.html", tenants=[tenant], users=users)
