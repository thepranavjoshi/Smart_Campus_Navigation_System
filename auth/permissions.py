"""
Permissions - Role-Based Access Control
Flask decorators for route protection
"""
from functools import wraps
from flask import session, redirect, url_for, flash, request


def login_required(f):
    """
    Decorator to require authentication
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not session.get('authenticated', False):
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def mfa_required(f):
    """
    Decorator to require MFA verification
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('mfa_verified', False):
            flash('Please complete MFA verification.', 'warning')
            return redirect(url_for('auth.verify_otp'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Decorator for admin-only routes
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        if session.get('role') != 'admin':
            flash('Access denied. Administrator privileges required.', 'danger')
            return redirect(url_for('dashboard.index'))
        
        return f(*args, **kwargs)
    return decorated_function


def faculty_required(f):
    """
    Decorator for faculty or higher routes
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        allowed_roles = ['admin', 'faculty', 'staff']
        if session.get('role') not in allowed_roles:
            flash('Access denied. Faculty privileges required.', 'danger')
            return redirect(url_for('dashboard.index'))
        
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    """
    Flexible decorator for multiple role access
    Usage: @role_required('admin', 'faculty')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            
            if session.get('role') not in roles:
                flash('Access denied. Insufficient privileges.', 'danger')
                return redirect(url_for('dashboard.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def visitor_allowed(f):
    """
    Decorator for routes accessible to all authenticated users including visitors
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def get_current_user_role():
    """
    Get the current user's role from session
    """
    return session.get('role', None)


def is_admin():
    """
    Check if current user is admin
    """
    return session.get('role') == 'admin'


def is_faculty():
    """
    Check if current user is faculty/staff
    """
    return session.get('role') in ['admin', 'faculty', 'staff']


def can_view_analytics():
    """
    Check if current user can view analytics
    """
    return session.get('role') == 'admin'


def can_manage_content():
    """
    Check if current user can manage content
    """
    return session.get('role') in ['admin', 'faculty', 'staff']
