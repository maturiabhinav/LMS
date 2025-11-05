from flask import request, g
from .models import Tenant
from .extensions import db

def load_tenant():
    """
    Resolve tenant from subdomain.
    If host is example: client.company.com -> subdomain is 'client'
    For localhost testing you may use 'client.localhost:5000' but many browsers behave differently.
    """
    g.tenant = None
    host = request.host.split(':')[0]  # remove port
    # allow local dev with SERVER_NAME not set
    parts = host.split('.')
    # If host has at least 3 parts assume subdomain exists
    if len(parts) >= 3:
        subdomain = parts[0]
        tenant = Tenant.query.filter_by(subdomain=subdomain).first()
        if tenant:
            g.tenant = tenant
    # else leave g.tenant as None (superadmin context or unknown host)
