"""
Time Utilities
Timestamp helpers for logging and tracking
"""
from datetime import datetime


def get_timestamp():
    """
    Get current timestamp in ISO format
    """
    return datetime.now().isoformat()


def get_formatted_timestamp():
    """
    Get human-readable timestamp
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_date():
    """
    Get current date string
    """
    return datetime.now().strftime("%Y-%m-%d")


def get_time():
    """
    Get current time string
    """
    return datetime.now().strftime("%H:%M:%S")


def parse_timestamp(timestamp_str):
    """
    Parse ISO format timestamp string to datetime
    """
    try:
        return datetime.fromisoformat(timestamp_str)
    except ValueError:
        return None


def get_hour():
    """
    Get current hour (0-23) for analytics
    """
    return datetime.now().hour


def format_datetime(dt):
    """
    Format datetime object for display
    """
    if dt is None:
        return ""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def time_difference_seconds(timestamp_str):
    """
    Calculate seconds since given timestamp
    """
    try:
        past = datetime.fromisoformat(timestamp_str)
        now = datetime.now()
        return (now - past).total_seconds()
    except Exception:
        return float('inf')
