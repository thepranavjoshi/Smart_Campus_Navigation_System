"""
Notification Engine
Rules, triggers, and notification management
"""
import config
from utils.csv_handler import read_csv, write_csv, append_csv, get_next_id, update_csv_row
from utils.time_utils import get_timestamp
import os


def get_user_notifications(user_id):
    """
    Get all notifications for a user
    """
    notifications = read_csv(config.NOTIFICATIONS_CSV)
    user_notifs = [n for n in notifications if str(n.get('user_id')) == str(user_id)]
    return user_notifs


def get_undelivered_notifications(user_id):
    """
    Get undelivered notifications for a user
    """
    notifications = get_user_notifications(user_id)
    return [n for n in notifications if n.get('delivered', '').lower() != 'true']


def create_notification(user_id, message):
    """
    Create a new notification
    """
    next_id = get_next_id(config.NOTIFICATIONS_CSV)
    
    notification = {
        'id': str(next_id),
        'user_id': str(user_id),
        'message': message,
        'delivered': 'False',
        'status': 'Pending'
    }
    
    fieldnames = ['id', 'user_id', 'message', 'delivered', 'status']
    if append_csv(config.NOTIFICATIONS_CSV, notification, fieldnames):
        log_notification(next_id, message, 'CREATED')
        return notification
    return None


def mark_delivered(notification_id):
    """
    Mark notification as delivered
    """
    update_csv_row(config.NOTIFICATIONS_CSV, 'id', notification_id, {'delivered': 'True'})
    log_notification(notification_id, '', 'DELIVERED')


def confirm_notification(notification_id):
    """
    Confirm notification status (admin action)
    """
    update_csv_row(config.NOTIFICATIONS_CSV, 'id', notification_id, {'status': 'Confirmed'})
    log_notification(notification_id, '', 'CONFIRMED')
    return True


def get_notification_by_id(notification_id):
    """
    Get a specific notification by ID
    """
    notifications = read_csv(config.NOTIFICATIONS_CSV)
    for notif in notifications:
        if str(notif.get('id')) == str(notification_id):
            return notif
    return None


def mark_all_delivered(user_id):
    """
    Mark all notifications for a user as delivered
    """
    notifications = read_csv(config.NOTIFICATIONS_CSV)
    updated = False
    
    for notif in notifications:
        if str(notif.get('user_id')) == str(user_id) and notif.get('delivered', '').lower() != 'true':
            notif['delivered'] = 'True'
            updated = True
    
    if updated:
        fieldnames = ['id', 'user_id', 'message', 'delivered']
        write_csv(config.NOTIFICATIONS_CSV, notifications, fieldnames)


def get_all_notifications():
    """
    Get all notifications (admin)
    """
    return read_csv(config.NOTIFICATIONS_CSV)


def get_notification_stats():
    """
    Get notification statistics
    """
    notifications = read_csv(config.NOTIFICATIONS_CSV)
    
    total = len(notifications)
    delivered = sum(1 for n in notifications if n.get('delivered', '').lower() == 'true')
    pending = total - delivered
    
    # Count by message type
    message_counts = {}
    for n in notifications:
        msg = n.get('message', 'Unknown')
        message_counts[msg] = message_counts.get(msg, 0) + 1
    
    return {
        'total': total,
        'delivered': delivered,
        'pending': pending,
        'delivery_rate': round(delivered / total * 100, 1) if total > 0 else 0,
        'by_type': message_counts
    }


def broadcast_notification(message, role=None):
    """
    Send notification to all users (optionally filtered by role)
    """
    users = read_csv(config.USERS_CSV)
    count = 0
    
    for user in users:
        if role is None or user.get('role', '').lower() == role.lower():
            create_notification(user.get('id'), message)
            count += 1
    
    return count


def log_notification(notification_id, message, status):
    """
    Log notification to alerts log
    """
    try:
        os.makedirs(config.LOGS_DIR, exist_ok=True)
        timestamp = get_timestamp()
        log_entry = f"[{timestamp}] Notification {notification_id}: {message[:50]}... - {status}\n"
        
        with open(config.ALERTS_LOG, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Error writing to alerts log: {e}")


def get_recent_notifications(limit=10):
    """
    Get most recent notifications
    """
    notifications = read_csv(config.NOTIFICATIONS_CSV)
    # Sort by id descending (assuming higher id = more recent)
    sorted_notifs = sorted(notifications, key=lambda x: int(x.get('id', 0)), reverse=True)
    return sorted_notifs[:limit]
