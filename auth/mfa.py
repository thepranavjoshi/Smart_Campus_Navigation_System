"""
MFA - Multi-Factor Authentication
OTP-based authentication via console/file simulation
"""
import random
import os
from datetime import datetime
from utils.time_utils import get_timestamp, time_difference_seconds
import config

# In-memory OTP storage (would use Redis/DB in production)
_otp_store = {}


def generate_otp():
    """
    Generate a 6-digit OTP
    """
    return str(random.randint(100000, 999999))


def save_otp(user_id, otp):
    """
    Store OTP with timestamp for validation
    Also prints to console and saves to file for simulation
    """
    timestamp = get_timestamp()
    _otp_store[str(user_id)] = {
        'otp': otp,
        'timestamp': timestamp
    }
    
    # Console simulation - print OTP
    print(f"\n{'='*50}")
    print(f"MFA OTP for User ID {user_id}: {otp}")
    print(f"Valid for {config.MFA_OTP_VALIDITY // 60} minutes")
    print(f"{'='*50}\n")
    
    # File simulation - save to logs
    try:
        os.makedirs(config.LOGS_DIR, exist_ok=True)
        otp_log_path = os.path.join(config.LOGS_DIR, 'otp_log.txt')
        with open(otp_log_path, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] User {user_id}: OTP = {otp}\n")
    except Exception as e:
        print(f"Could not write OTP to file: {e}")
    
    return True


def verify_otp(user_id, entered_otp):
    """
    Validate OTP entered by user
    Returns: True if valid, False otherwise
    """
    user_id = str(user_id)
    
    if user_id not in _otp_store:
        return False
    
    stored = _otp_store[user_id]
    
    # Check if OTP has expired
    seconds_elapsed = time_difference_seconds(stored['timestamp'])
    if seconds_elapsed > config.MFA_OTP_VALIDITY:
        # OTP expired, remove it
        del _otp_store[user_id]
        return False
    
    # Check if OTP matches
    if stored['otp'] == str(entered_otp):
        # Valid OTP, remove it (single use)
        del _otp_store[user_id]
        return True
    
    return False


def clear_otp(user_id):
    """
    Clear OTP for a user (e.g., on logout)
    """
    user_id = str(user_id)
    if user_id in _otp_store:
        del _otp_store[user_id]


def get_otp_status(user_id):
    """
    Check if user has a pending OTP
    """
    user_id = str(user_id)
    if user_id not in _otp_store:
        return None
    
    stored = _otp_store[user_id]
    seconds_elapsed = time_difference_seconds(stored['timestamp'])
    
    if seconds_elapsed > config.MFA_OTP_VALIDITY:
        del _otp_store[user_id]
        return None
    
    return {
        'pending': True,
        'expires_in': config.MFA_OTP_VALIDITY - int(seconds_elapsed)
    }
