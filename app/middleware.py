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
    
    # If no BASE_DOMAIN configured or we're on Render's default domain, use path-based
    if not base or ".onrender.com" in host:
        # For Render deployment, we'll use path-based tenancy initially
        # You can configure custom domains later
        return
    
    # For custom domain setup
    if host == base:
        # Root domain - super admin
        return
        
    if host.endswith("." + base):
        # Subdomain like client1.ourcompany.com
        subdomain = host.replace("." + base, "").split('.')[-1]
        tenant = Tenant.query.filter_by(subdomain=subdomain).first()
        if tenant:
            g.tenant = tenant

