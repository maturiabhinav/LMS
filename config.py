import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY") or "dev-secret-key"
    
    # Database configuration
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if DATABASE_URL:
        # For psycopg3, the URL format is different
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
        elif DATABASE_URL.startswith("postgresql://"):
            DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
        
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Fallback for development
        SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Domain settings
    BASE_DOMAIN = os.getenv("BASE_DOMAIN", "localhost")
    SESSION_COOKIE_DOMAIN = os.getenv("SESSION_COOKIE_DOMAIN")
    SERVER_NAME = os.getenv("SERVER_NAME")
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "True").lower() in ("1","true","yes")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"