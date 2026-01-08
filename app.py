"""
Smart Campus Navigation System (SCNS)
Flask Application Entry Point
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, redirect, url_for, session, render_template
import config

# Initialize Flask app
app = Flask(__name__,
            static_folder=config.STATIC_DIR,
            template_folder=config.TEMPLATES_DIR)

# Load configuration
app.secret_key = config.SECRET_KEY
app.config['SESSION_TYPE'] = config.SESSION_TYPE
app.config['PERMANENT_SESSION_LIFETIME'] = config.PERMANENT_SESSION_LIFETIME

# Ensure required directories exist
os.makedirs(config.LOGS_DIR, exist_ok=True)
os.makedirs(os.path.join(config.STATIC_DIR, 'images', 'charts'), exist_ok=True)

# Register Blueprints
from auth import auth_bp
from navigation import navigation_bp
from dashboard import dashboard_bp

app.register_blueprint(auth_bp)
app.register_blueprint(navigation_bp)
app.register_blueprint(dashboard_bp)


# Root route
@app.route('/')
def index():
    """
    Show landing page or redirect to dashboard if authenticated
    """
    if session.get('authenticated'):
        return redirect(url_for('dashboard.index'))
    return render_template('landing.html')


# Context processor to add variables to all templates
@app.context_processor
def inject_user():
    """
    Inject user info into all templates
    """
    from notifications.engine import get_undelivered_notifications
    
    notification_count = 0
    if session.get('user_id'):
        notifications = get_undelivered_notifications(session.get('user_id'))
        notification_count = len(notifications)
    
    return {
        'notification_count': notification_count
    }


# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return '''
    <div style="text-align:center; padding:50px; font-family:sans-serif;">
        <h1>404 - Page Not Found</h1>
        <p>The requested page could not be found.</p>
        <a href="/" style="color:#6366f1;">Return Home</a>
    </div>
    ''', 404


@app.errorhandler(500)
def internal_error(e):
    return '''
    <div style="text-align:center; padding:50px; font-family:sans-serif;">
        <h1>500 - Internal Server Error</h1>
        <p>Something went wrong on our end.</p>
        <a href="/" style="color:#6366f1;">Return Home</a>
    </div>
    ''', 500


# Main entry point
if __name__ == '__main__':
    print("\n" + "="*60)
    print("Smart Campus Navigation System (SCNS)")
    print("="*60)
    print(f"Access the application at: http://127.0.0.1:5000")
    print(f"Project directory: {config.BASE_DIR}")
    print("="*60 + "\n")
    
    # Run Flask development server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
