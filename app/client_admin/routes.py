from flask import Blueprint, render_template, request, redirect, url_for, flash
from application import db
from app.models import Employee, ClientAdmin
from flask import current_app

client_admin_bp = Blueprint("client_admin", __name__)

@client_admin_bp.route("/dashboard")
def dashboard():
    return render_template("client_admin/dashboard.html")

@client_admin_bp.route("/create-employee", methods=["GET", "POST"])
def create_employee():
    if request.method == "POST":
        name = request.form["name"]
        role = request.form["role"]
        email = request.form["email"]
        client_id = 1  # This will be dynamic later based on logged-in client
        emp = Employee(name=name, role=role, email=email, client_id=client_id)
        db.session.add(emp)
        db.session.commit()
        flash("Employee created successfully!", "success")
        return redirect(url_for("client_admin.dashboard"))
    return render_template("client_admin/create_employee.html")
