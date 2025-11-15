import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY") or "dev-secret-key"
    
    # Database configuration - handle both build and runtime
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL:
        # Convert postgres:// to postgresql:// for SQLAlchemy
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Fallback for build process - use a dummy URL
        SQLALCHEMY_DATABASE_URI = "sqlite:///temp.db"
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Domain settings
    BASE_DOMAIN = os.getenv("BASE_DOMAIN", "localhost")
    SESSION_COOKIE_DOMAIN = os.getenv("SESSION_COOKIE_DOMAIN")
    SERVER_NAME = os.getenv("SERVER_NAME")
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "True").lower() in ("1","true","yes")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"