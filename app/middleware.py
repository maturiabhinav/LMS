from flask import request, g, current_app
from .models import Tenant
from .extensions import db

def load_tenant():
    """
    Resolve tenant from subdomain like abc.xyz.com.
    If no tenant detected, g.tenant is None (super-admin context).
    """
    g.tenant = None
    host = request.host.split(':')[0]  # remove port
    base = current_app.config.get("BASE_DOMAIN")
    if not base:
        return
    # If host equals base (xyz.com) -> superadmin root
    if host == base or host.endswith("." + base) is False:
        # host could be xyz.com or some other host (e.g. onrender.com) — attempt fallback:
        # If running on a platform default domain (e.g. xyz.onrender.com) we will support path fallback elsewhere.
        return

    # For a host like abc.xyz.com, take first label
    parts = host.split('.')
    if len(parts) >= 3:
        subdomain = parts[0]
        tenant = Tenant.query.filter_by(subdomain=subdomain).first()
        if tenant:
            g.tenant = tenant
