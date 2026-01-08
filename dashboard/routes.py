"""
Dashboard Routes
Role-specific dashboard pages
"""
from flask import render_template, session, redirect, url_for, flash, request
from dashboard import dashboard_bp
from dashboard.widgets import (
    get_admin_widgets,
    get_faculty_widgets,
    get_student_widgets,
    get_visitor_widgets,
    get_notification_widget
)
from auth.permissions import login_required, admin_required, faculty_required
from analytics.visualisations import generate_all_charts, generate_plotly_dashboard
from analytics.metrics import get_usage_stats, get_building_stats, get_peak_times
from notifications.engine import get_user_notifications, mark_all_delivered
from users.models import get_all_users, get_user_by_id
from users.services import (
    create_user_admin, 
    delete_user, 
    update_user_role, 
    get_user_stats as get_user_role_stats
)


@dashboard_bp.route('/')
@login_required
def index():
    """
    Main dashboard - routes to role-specific dashboard
    """
    role = session.get('role', 'visitor')
    
    if role == 'admin':
        return redirect(url_for('dashboard.admin_dashboard'))
    elif role in ['faculty', 'staff']:
        return redirect(url_for('dashboard.faculty_dashboard'))
    elif role == 'student':
        return redirect(url_for('dashboard.student_dashboard'))
    else:
        return redirect(url_for('dashboard.visitor_dashboard'))


@dashboard_bp.route('/admin')
@admin_required
def admin_dashboard():
    """
    Admin dashboard with full analytics
    """
    widgets = get_admin_widgets()
    charts = generate_all_charts()
    plotly_charts = generate_plotly_dashboard()
    building_stats = get_building_stats()
    
    return render_template('dashboard_admin.html',
                         widgets=widgets,
                         charts=charts,
                         plotly_charts=plotly_charts,
                         building_stats=building_stats)


@dashboard_bp.route('/faculty')
@faculty_required
def faculty_dashboard():
    """
    Faculty dashboard with content management
    """
    widgets = get_faculty_widgets()
    user_id = session.get('user_id')
    notifications = get_notification_widget(user_id)
    
    return render_template('dashboard_faculty.html',
                         widgets=widgets,
                         notifications=notifications)


@dashboard_bp.route('/student')
@login_required
def student_dashboard():
    """
    Student dashboard with navigation and notifications
    """
    user_id = session.get('user_id')
    widgets = get_student_widgets(user_id)
    notifications = get_notification_widget(user_id)
    
    return render_template('dashboard_student.html',
                         widgets=widgets,
                         notifications=notifications)


@dashboard_bp.route('/visitor')
@login_required
def visitor_dashboard():
    """
    Visitor dashboard with limited navigation
    """
    widgets = get_visitor_widgets()
    
    return render_template('dashboard_visitor.html',
                         widgets=widgets)


@dashboard_bp.route('/notifications')
@login_required
def view_notifications():
    """
    View all notifications for current user
    """
    user_id = session.get('user_id')
    notifications = get_user_notifications(user_id)
    
    return render_template('notifications.html', notifications=notifications)


@dashboard_bp.route('/notifications/mark-read')
@login_required
def mark_notifications_read():
    """
    Mark all notifications as read
    """
    user_id = session.get('user_id')
    mark_all_delivered(user_id)
    flash('All notifications marked as read.', 'success')
    return redirect(url_for('dashboard.view_notifications'))


@dashboard_bp.route('/users')
@admin_required
def manage_users():
    """
    User management page (admin only)
    """
    users = get_all_users()
    stats = get_user_role_stats()
    
    return render_template('manage_users.html', users=users, stats=stats)


@dashboard_bp.route('/users/create', methods=['GET', 'POST'])
@admin_required
def create_user_page():
    """
    Create new user (admin only)
    """
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        role = request.form.get('role', 'visitor')
        
        user, error = create_user_admin(username, email, role)
        
        if error:
            flash(error, 'danger')
        else:
            flash(f'User {username} created successfully.', 'success')
            return redirect(url_for('dashboard.manage_users'))
    
    return render_template('create_user.html')


@dashboard_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user_page(user_id):
    """
    Delete user (admin only)
    """
    admin_id = session.get('user_id')
    success, error = delete_user(user_id, admin_id)
    
    if error:
        flash(error, 'danger')
    else:
        flash('User deleted successfully.', 'success')
    
    return redirect(url_for('dashboard.manage_users'))


@dashboard_bp.route('/analytics')
@admin_required
def analytics():
    """
    Full analytics page (admin only)
    """
    usage_stats = get_usage_stats()
    building_stats = get_building_stats()
    peak_times = get_peak_times()
    charts = generate_all_charts()
    plotly_charts = generate_plotly_dashboard()
    
    return render_template('analytics.html',
                         usage_stats=usage_stats,
                         building_stats=building_stats,
                         peak_times=peak_times,
                         charts=charts,
                         plotly_charts=plotly_charts)


# ========== FACULTY CONTENT MANAGEMENT ==========

@dashboard_bp.route('/content')
@faculty_required
def content_management():
    """
    Content management page (Faculty and Admin only)
    """
    from notifications.engine import get_all_notifications, get_notification_stats
    from utils.csv_handler import read_csv
    import config
    
    notifications = get_all_notifications()[-20:]  # Last 20
    notif_stats = get_notification_stats()
    routes = read_csv(config.ROUTES_CSV)[:20]  # First 20 routes
    
    return render_template('content_management.html',
                         notifications=notifications,
                         notif_stats=notif_stats,
                         routes=routes)


@dashboard_bp.route('/content/notification/add', methods=['GET', 'POST'])
@faculty_required
def add_notification():
    """
    Add new notification (Faculty and Admin)
    """
    from notifications.engine import create_notification, broadcast_notification
    from users.models import get_all_users
    
    if request.method == 'POST':
        message = request.form.get('message', '').strip()
        target = request.form.get('target', 'all')
        user_id = request.form.get('user_id', '')
        
        if not message:
            flash('Please enter a notification message.', 'warning')
            return render_template('add_notification.html', users=get_all_users())
        
        if target == 'all':
            count = broadcast_notification(message)
            flash(f'Notification sent to {count} users.', 'success')
        elif target == 'role':
            role = request.form.get('role', 'student')
            count = broadcast_notification(message, role=role)
            flash(f'Notification sent to {count} {role}s.', 'success')
        elif target == 'user' and user_id:
            create_notification(user_id, message)
            flash('Notification sent to user.', 'success')
        else:
            flash('Invalid notification target.', 'danger')
        
        return redirect(url_for('dashboard.content_management'))
    
    users = get_all_users()
    return render_template('add_notification.html', users=users)


@dashboard_bp.route('/content/notification/delete/<int:notif_id>', methods=['POST'])
@faculty_required
def delete_notification(notif_id):
    """
    Delete notification (Faculty and Admin)
    """
    from utils.csv_handler import delete_csv_row
    import config
    
    if delete_csv_row(config.NOTIFICATIONS_CSV, 'id', notif_id):
        flash('Notification deleted.', 'success')
    else:
        flash('Failed to delete notification.', 'danger')
    
    return redirect(url_for('dashboard.content_management'))


@dashboard_bp.route('/notifications/confirm/<int:notif_id>', methods=['GET'])
@faculty_required
def confirm_notification(notif_id):
    """
    Confirm notification status (Faculty and Admin)
    """
    from notifications.engine import confirm_notification
    
    if confirm_notification(notif_id):
        flash('Notification confirmed.', 'success')
    else:
        flash('Failed to confirm notification.', 'danger')
    
    return redirect(url_for('dashboard.content_management'))
