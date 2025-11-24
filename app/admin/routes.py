from flask import Blueprint, render_template, request, redirect, url_for, flash, g, abort
from flask_login import login_required, current_user
from ..extensions import db
from ..models import User, RoleEnum, Student, Tenant
import random
import string

admin_bp = Blueprint("admin", __name__, template_folder="templates", static_folder="static")

def require_client_admin(fn):
    from functools import wraps
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        # Allow client admins and super admins
        if current_user.role not in (RoleEnum.CLIENT_ADMIN, RoleEnum.SUPER_ADMIN):
            abort(403)
        return fn(*args, **kwargs)
    return wrapped

@admin_bp.route("/admin/dashboard")
@login_required
@require_client_admin
def dashboard():
    tenant = g.tenant or current_user.tenant
    total_students = Student.query.filter_by(tenant_id=tenant.id).count()
    recent_students = Student.query.filter_by(tenant_id=tenant.id).order_by(Student.registration_date.desc()).limit(5).all()
    
    return render_template("admin/dashboard.html", 
                         tenant=tenant,
                         total_students=total_students,
                         recent_students=recent_students)

@admin_bp.route("/admin/students")
@login_required
@require_client_admin
def students():
    tenant = g.tenant or current_user.tenant
    students_list = Student.query.filter_by(tenant_id=tenant.id).order_by(Student.registration_date.desc()).all()
    return render_template("admin/students.html", students=students_list, tenant=tenant)

@admin_bp.route("/admin/create-student", methods=["GET", "POST"])
@login_required
@require_client_admin
def create_student():
    tenant = g.tenant or current_user.tenant
    if request.method == "POST":
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        course_enrolled = request.form.get("course_enrolled")
        
        student = Student(
            student_id=generate_student_id(),
            full_name=full_name,
            email=email,
            phone=phone,
            course_enrolled=course_enrolled,
            tenant_id=tenant.id
        )
        db.session.add(student)
        db.session.commit()
        flash(f"Student '{full_name}' created successfully with ID: {student.student_id}", "success")
        return redirect(url_for("admin.students"))
    
    return render_template("admin/create_student.html", tenant=tenant)
