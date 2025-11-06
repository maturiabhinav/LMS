"""
Run: python scripts/seed_superadmin.py
This script uses DATABASE_URL and SUPERADMIN_EMAIL / SUPERADMIN_PASSWORD env vars.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import db
from app.models import User, RoleEnum

app = create_app()
with app.app_context():
    email = os.getenv("SUPERADMIN_EMAIL")
    password = os.getenv("SUPERADMIN_PASSWORD")
    if not email or not password:
        raise RuntimeError("Set SUPERADMIN_EMAIL and SUPERADMIN_PASSWORD as env vars")
    existing = User.query.filter_by(email=email, role=RoleEnum.SUPER_ADMIN).first()
    if existing:
        print("Super admin already exists:", email)
    else:
        admin = User(email=email, full_name="Super Admin", role=RoleEnum.SUPER_ADMIN)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        print("Created super admin:", email)
