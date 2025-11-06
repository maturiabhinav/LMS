from flask import Blueprint, render_template

employee_bp = Blueprint("employee", __name__)

@employee_bp.route("/dashboard")
def dashboard():
    return render_template("employee/dashboard.html")
