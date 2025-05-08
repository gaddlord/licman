"""
Flexible authentication module that can either:
1. Skip authentication completely (based on SKIP_AUTH env variable)
2. Use OpenID authentication (production)
3. Use development authentication (for testing)
"""
import os
from functools import wraps
from flask import Flask, redirect, request, url_for, session, g
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if authentication should be skipped
SKIP_AUTH = os.getenv('SKIP_AUTH', 'false').lower() == 'true'

# Determine which authentication to use
USE_DEV_AUTH = True  # Set to False for production with PingOne

def init_flexible_auth(app):
    """Initialize the appropriate authentication system"""
    # Make authentication configuration available to templates
    app.config['SKIP_AUTH'] = SKIP_AUTH
    app.config['USE_DEV_AUTH'] = USE_DEV_AUTH
    
    if SKIP_AUTH:
        # No authentication - just set up a mock user for templates
        @app.before_request
        def set_mock_user():
            # Create a mock admin user that's always logged in
            g.user = {
                'name': 'Admin User',
                'email': 'admin@example.com',
                'sub': 'admin-user',
                'preferred_username': 'admin'
            }
        
        print("WARNING: Authentication is DISABLED. This should only be used in development.")
        return app
    elif USE_DEV_AUTH:
        # Use development authentication
        from dev_auth import init_dev_auth
        return init_dev_auth(app)
    else:
        # Use OpenID authentication
        from auth import init_auth
        return init_auth(app)

def flexible_login_required(f):
    """
    Decorator that either:
    1. Does nothing if SKIP_AUTH is true
    2. Requires login otherwise
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if SKIP_AUTH:
            # Skip authentication check
            return f(*args, **kwargs)
        
        # Use the appropriate login_required based on configuration
        if USE_DEV_AUTH:
            from dev_auth import login_required
        else:
            from auth import login_required
            
        # Apply the actual login_required decorator
        return login_required(f)(*args, **kwargs)
    
    return decorated_function
