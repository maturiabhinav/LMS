import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY") or "dev-secret-key"
    
    # FORCE PostgreSQL - Render always provides DATABASE_URL
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL environment variable is required")
    
    # Convert postgres:// to postgresql:// for SQLAlchemy
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Domain settings
    BASE_DOMAIN = os.getenv("BASE_DOMAIN", "localhost")
    SESSION_COOKIE_DOMAIN = os.getenv("SESSION_COOKIE_DOMAIN")
    SERVER_NAME = os.getenv("SERVER_NAME")
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "True").lower() in ("1","true","yes")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"