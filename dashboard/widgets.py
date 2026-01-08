"""
Dashboard Widgets
Charts and summary components for dashboard
"""
from analytics.metrics import (
    get_usage_stats,
    get_user_stats,
    get_notification_stats,
    get_popular_locations,
    get_accessibility_stats,
    get_peak_times
)
from notifications.engine import get_recent_notifications, get_undelivered_notifications
from users.models import get_all_users


def get_quick_stats():
    """
    Get quick statistics for dashboard header
    """
    usage = get_usage_stats()
    notif = get_notification_stats()
    
    return {
        'total_users': usage['total_users'],
        'total_locations': usage['total_locations'],
        'total_routes': usage['total_routes'],
        'notification_delivery_rate': notif['delivery_rate'],
        'pending_notifications': notif['pending']
    }


def get_admin_widgets():
    """
    Get all widgets for admin dashboard
    """
    return {
        'quick_stats': get_quick_stats(),
        'user_stats': get_user_stats(),
        'notification_stats': get_notification_stats(),
        'popular_locations': get_popular_locations()[:5],
        'accessibility': get_accessibility_stats(),
        'recent_notifications': get_recent_notifications(5)
    }


def get_faculty_widgets():
    """
    Get widgets for faculty dashboard
    """
    return {
        'quick_stats': get_quick_stats(),
        'recent_notifications': get_recent_notifications(5),
        'popular_locations': get_popular_locations()[:5]
    }


def get_student_widgets(user_id):
    """
    Get widgets for student dashboard
    """
    return {
        'notifications': get_undelivered_notifications(user_id),
        'popular_locations': get_popular_locations()[:3]
    }


def get_visitor_widgets():
    """
    Get widgets for visitor dashboard (limited)
    """
    return {
        'popular_locations': get_popular_locations()[:3]
    }


def get_notification_widget(user_id):
    """
    Get notification widget for any user
    """
    notifications = get_undelivered_notifications(user_id)
    return {
        'count': len(notifications),
        'notifications': notifications[:5]
    }


def get_navigation_quick_links():
    """
    Get quick navigation links
    """
    locations = get_popular_locations()[:4]
    return [loc[0] for loc in locations]
