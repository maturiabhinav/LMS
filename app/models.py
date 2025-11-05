import enum
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db
from flask_login import UserMixin

class RoleEnum(enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    CLIENT_ADMIN = "CLIENT_ADMIN"
    EMPLOYEE = "EMPLOYEE"

class Tenant(db.Model):
    __tablename__ = "tenants"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    subdomain = db.Column(db.String(128), unique=True, nullable=False)
    slug = db.Column(db.String(128), unique=True, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    users = db.relationship("User", back_populates="tenant", lazy="dynamic")

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(256))
    role = db.Column(db.Enum(RoleEnum), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tenant = db.relationship("Tenant", back_populates="users")

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)

    def get_id(self):
        return str(self.id)
