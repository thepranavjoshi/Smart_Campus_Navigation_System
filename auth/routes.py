"""
Authentication Routes
Login, Register, Logout, MFA verification
Uses original CSV format - no password hashing
"""
from flask import render_template, request, redirect, url_for, flash, session
from auth import auth_bp
from auth.mfa import generate_otp, save_otp, verify_otp
from users.models import authenticate_user, create_user, get_user_by_id
from utils.time_utils import get_timestamp
import os
import config


def log_activity(user_id, action, details=''):
    """
    Log user activity
    """
    try:
        os.makedirs(config.LOGS_DIR, exist_ok=True)
        timestamp = get_timestamp()
        log_entry = f"[{timestamp}] User {user_id}: {action} - {details}\n"
        
        with open(config.ACTIVITY_LOG, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Error writing to activity log: {e}")


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login page - uses username from original CSV
    """
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')  # Optional password
        
        if not username:
            flash('Please enter your username.', 'warning')
            return render_template('login.html')
        
        user, error = authenticate_user(username, password)
        
        if error:
            flash(error, 'danger')
            log_activity(0, 'LOGIN_FAILED', f"Username: {username}")
            return render_template('login.html')
        
        # Store user in session (pending MFA)
        session['pending_user_id'] = user.id
        session['pending_username'] = user.username
        session['pending_role'] = user.role
        
        # Generate and send OTP
        otp = generate_otp()
        save_otp(user.id, otp)
        
        log_activity(user.id, 'LOGIN_INITIATED', f"MFA pending for {username}")
        
        flash('Please enter the OTP shown in the console.', 'info')
        return redirect(url_for('auth.verify_otp_page'))
    
    return render_template('login.html')


@auth_bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp_page():
    """
    MFA OTP verification page
    """
    if 'pending_user_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        entered_otp = request.form.get('otp', '').strip()
        user_id = session.get('pending_user_id')
        
        if verify_otp(user_id, entered_otp):
            # MFA successful - complete login
            session['user_id'] = session.pop('pending_user_id')
            session['username'] = session.pop('pending_username')
            session['role'] = session.pop('pending_role')
            session['authenticated'] = True
            session['mfa_verified'] = True
            
            log_activity(session['user_id'], 'LOGIN_SUCCESS', 'MFA verified')
            
            flash(f'Welcome, {session["username"]}!', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid or expired OTP. Please try again.', 'danger')
            log_activity(user_id, 'MFA_FAILED', 'Invalid OTP entered')
            
            # Generate new OTP
            otp = generate_otp()
            save_otp(user_id, otp)
    
    return render_template('verify_otp.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    New user registration - adds to original CSV format
    """
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        consent = request.form.get('consent') == 'on'
        
        # Validation
        if not all([username, email]):
            flash('Please fill in username and email.', 'warning')
            return render_template('register.html')
        
        if password and password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')
        
        if not consent:
            flash('You must agree to the terms and privacy policy.', 'warning')
            return render_template('register.html')
        
        # Get role from form (defaults to 'visitor' if not provided)
        role = request.form.get('role', 'visitor')
        valid_roles = ['admin', 'faculty', 'student', 'visitor']
        if role not in valid_roles:
            role = 'visitor'
        
        # Create user with selected role
        # Data is added to scns_users.csv
        user, error = create_user(username, email, password, role=role)
        
        if error:
            flash(error, 'danger')
            return render_template('register.html')
        
        log_activity(user.id, 'REGISTER', f"New user registered: {username}")
        
        flash('Registration successful! Please log in with your username.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')


@auth_bp.route('/logout')
def logout():
    """
    User logout
    """
    user_id = session.get('user_id', 0)
    username = session.get('username', 'Unknown')
    
    if user_id:
        log_activity(user_id, 'LOGOUT', f"User {username} logged out")
    
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/resend-otp')
def resend_otp():
    """
    Resend OTP
    """
    if 'pending_user_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('auth.login'))
    
    user_id = session['pending_user_id']
    otp = generate_otp()
    save_otp(user_id, otp)
    
    log_activity(user_id, 'RESEND_OTP', 'New OTP generated')
    
    flash('A new OTP has been sent. Check the console.', 'info')
    return redirect(url_for('auth.verify_otp_page'))
