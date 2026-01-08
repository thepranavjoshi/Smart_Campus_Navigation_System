"""
Notification Logger
Alert logs and delivery status tracking
"""
import config
from utils.csv_handler import read_csv
from utils.time_utils import get_timestamp, get_formatted_timestamp
import os


def log_alert(notification_id, user_id, message, status):
    """
    Log notification alert with full details
    """
    try:
        os.makedirs(config.LOGS_DIR, exist_ok=True)
        timestamp = get_formatted_timestamp()
        log_entry = f"[{timestamp}] ID:{notification_id} | User:{user_id} | Status:{status} | {message}\n"
        
        with open(config.ALERTS_LOG, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        return True
    except Exception as e:
        print(f"Error writing alert log: {e}")
        return False


def get_delivery_status(notification_id):
    """
    Get delivery status of a specific notification
    """
    notifications = read_csv(config.NOTIFICATIONS_CSV)
    for notif in notifications:
        if str(notif.get('id')) == str(notification_id):
            return {
                'id': notification_id,
                'delivered': notif.get('delivered', '').lower() == 'true',
                'message': notif.get('message', '')
            }
    return None


def get_alert_log_entries(limit=50):
    """
    Read recent alert log entries
    """
    try:
        if not os.path.exists(config.ALERTS_LOG):
            return []
        
        with open(config.ALERTS_LOG, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Return last N entries (reverse order)
        return [line.strip() for line in reversed(lines[-limit:])]
    except Exception as e:
        print(f"Error reading alert log: {e}")
        return []


def get_delivery_statistics():
    """
    Calculate delivery statistics from notifications
    """
    notifications = read_csv(config.NOTIFICATIONS_CSV)
    
    if not notifications:
        return {
            'total': 0,
            'delivered': 0,
            'pending': 0,
            'rate': 0
        }
    
    total = len(notifications)
    delivered = sum(1 for n in notifications if n.get('delivered', '').lower() == 'true')
    
    return {
        'total': total,
        'delivered': delivered,
        'pending': total - delivered,
        'rate': round(delivered / total * 100, 1)
    }


def search_alerts(query):
    """
    Search alert logs for specific content
    """
    entries = get_alert_log_entries(limit=200)
    return [entry for entry in entries if query.lower() in entry.lower()]
