import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY") or "dev-secret"
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")  # required
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Domain / cookie settings for subdomain sessions (set on Render)
    BASE_DOMAIN = os.getenv("BASE_DOMAIN")  # e.g. xyz.com
    SESSION_COOKIE_DOMAIN = os.getenv("SESSION_COOKIE_DOMAIN")  # e.g. .xyz.com
    SERVER_NAME = os.getenv("SERVER_NAME")  # e.g. xyz.com
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "True").lower() in ("1","true","yes")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
