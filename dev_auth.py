"""
Development authentication module for testing without PingOne.
This should NEVER be used in production.
"""
from flask import redirect, url_for, session, g, Blueprint, render_template, request
from functools import wraps

dev_auth = Blueprint('dev_auth', __name__)

@dev_auth.route('/dev-login', methods=['GET', 'POST'])
def dev_login():
    """Development login page for testing"""
    if request.method == 'POST':
        username = request.form.get('username')
        if username:
            # Create a mock user session
            session['user'] = {
                'name': username,
                'email': f"{username}@example.com",
                'sub': f"dev-user-{username}",
                'preferred_username': username
            }
            return redirect('/')
    return render_template('dev_login.html')

@dev_auth.route('/dev-logout')
def dev_logout():
    """Development logout for testing"""
    session.pop('user', None)
    return redirect('/')

def init_dev_auth(app):
    """Initialize development authentication"""
    app.register_blueprint(dev_auth)
    
    @app.before_request
    def load_user():
        g.user = session.get('user')
    
    return app

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('dev_auth.dev_login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function
