import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY") or "dev-secret-key"
    
    # Database configuration
    if os.getenv("DATABASE_URL"):
        SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///multi_tenant.db"
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Domain settings - don't set SERVER_NAME for production
    BASE_DOMAIN = os.getenv("BASE_DOMAIN", "localhost")
    SESSION_COOKIE_DOMAIN = os.getenv("SESSION_COOKIE_DOMAIN")
    # Remove SERVER_NAME or make it conditional
    SERVER_NAME = os.getenv("SERVER_NAME")  # This can be None
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False").lower() in ("1","true","yes")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"