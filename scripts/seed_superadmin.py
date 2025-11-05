"""
Script to create default super-admin user.
Run: python scripts/seed_superadmin.py
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import db
from app.models import User, RoleEnum
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    email = "admin@company.com"
    if User.query.filter_by(email=email).first():
        print("Super admin already exists")
    else:
        u = User(email=email, full_name="Super Admin", role=RoleEnum.SUPER_ADMIN)
        u.set_password("SuperSecurePass123!")
        db.session.add(u)
        db.session.commit()
        print("Created super admin:", email)
