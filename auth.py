import json
import os
import logging
from functools import wraps
from flask import Flask, redirect, request, url_for, session, g
from authlib.integrations.flask_client import OAuth
import requests

# Set to True for development, False for production
DEVELOPMENT_MODE = True

def init_auth(app):
    # Load the OpenID Connect configuration
    with open('oidc_config.json', 'r') as f:
        config = json.load(f)['web']
    
    # Configure Flask app for sessions
    app.secret_key = os.environ.get('SECRET_KEY', 'dev_secret_key')  # Use a secure key in production
    
    # Initialize OAuth
    oauth = OAuth(app)
    
    # Register PingOne as an OAuth provider
    client_kwargs = {
        'scope': 'openid email profile'
    }
    
    # In development mode, disable SSL verification
    if DEVELOPMENT_MODE:
        client_kwargs['verify'] = False
        # Suppress insecure request warnings in development
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        logging.warning('SSL verification disabled. DO NOT USE IN PRODUCTION!')
    
    oauth.register(
        name='pingone',
        client_id=config['client_id'],
        client_secret=config['client_secret'],
        server_metadata_url=f"{config['issuer']}/.well-known/openid-configuration",
        client_kwargs=client_kwargs
    )
    
    # Store OAuth in app context
    app.oauth = oauth
    
    # Authentication routes
    @app.route('/login')
    def login():
        redirect_uri = url_for('callback', _external=True)
        return oauth.pingone.authorize_redirect(redirect_uri)
    
    @app.route('/callback')
    def callback():
        token = oauth.pingone.authorize_access_token()
        user_info = oauth.pingone.parse_id_token(token)
        session['user'] = user_info
        return redirect('/')
    
    @app.route('/logout')
    def logout():
        session.pop('user', None)
        return redirect('/')
    
    @app.before_request
    def load_user():
        g.user = session.get('user')
    
    return app

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function
