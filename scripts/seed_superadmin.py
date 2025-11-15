"""
Run: python scripts/seed_superadmin.py
This script uses DATABASE_URL and SUPERADMIN_EMAIL / SUPERADMIN_PASSWORD env vars.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import db
from app.models import User, RoleEnum

try:
    app = create_app()
    
    with app.app_context():
        email = os.getenv("SUPERADMIN_EMAIL")
        password = os.getenv("SUPERADMIN_PASSWORD")
        
        if not email or not password:
            print("Warning: SUPERADMIN_EMAIL and SUPERADMIN_PASSWORD not set")
            sys.exit(0)  # Exit gracefully, don't fail build
            
        # Check if database is accessible
        try:
            # Try to query the database
            User.query.count()
            print("Database is accessible")
        except Exception as e:
            print(f"Database not accessible: {e}")
            print("Skipping super admin creation - database might not be ready")
            sys.exit(0)
        
        # Check if super admin already exists
        existing = User.query.filter_by(email=email, role=RoleEnum.SUPER_ADMIN).first()
        if existing:
            print("Super admin already exists:", email)
            # Update password if it's different
            if not existing.check_password(password):
                existing.set_password(password)
                db.session.commit()
                print("Super admin password updated")
        else:
            admin = User(email=email, full_name="Super Admin", role=RoleEnum.SUPER_ADMIN)
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()
            print("Created super admin:", email)
            
        # Print all users for debugging
        print("Current users in database:")
        users = User.query.all()
        for user in users:
            print(f"- {user.email} (Role: {user.role.value}, Tenant: {user.tenant_id})")
            
except Exception as e:
    print(f"Error during super admin seeding: {e}")
    print("Continuing build process...")
    sys.exit(0)  # Don't fail the build