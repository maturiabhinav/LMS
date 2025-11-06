1) Push to GitHub.
2) On Render: New Web Service -> Connect repo.
3) Set Environment Variables (see list in repo).
4) Provision Postgres or use Render Postgres and set DATABASE_URL.
5) Deploy.
6) In Render service -> Shell run:
   flask db init
   flask db migrate -m "init"
   flask db upgrade
   python scripts/seed_superadmin.py
7) Add Custom Domain: add `xyz.com` and `*.xyz.com` (Render supports wildcard). Add DNS CNAME records Render shows in your registrar; wait for verification.
8) Visit https://abc.xyz.com -> login at /auth/login using user created by seed script.
