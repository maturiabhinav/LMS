# Multi-tenant Flask App (superadmin + tenant subdomains)

## Quick local run
1. Create virtualenv and install requirements:
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

2. Copy .env.example to .env and edit as needed.

3. Initialize DB (with sqlite default):
   export FLASK_APP=app.py
   flask db init
   flask db migrate -m "init"
   flask db upgrade

4. Seed superadmin:
   python scripts/seed_superadmin.py

5. Run:
   python app.py

## Deployment (Railway)
- Push to GitHub and connect Railway.
- Set `DATABASE_URL`, `SECRET_KEY`, `SESSION_COOKIE_DOMAIN` (e.g. .company.com), and optional `SERVER_NAME`.
- Add custom domain and wildcard domain entries in Railway and add corresponding CNAME in your DNS provider for wildcard `*`.
