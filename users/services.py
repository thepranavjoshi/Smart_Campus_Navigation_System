"""
User Services
Admin-only user management operations
Uses original CSV format
"""
import config
from utils.csv_handler import read_csv, write_csv, delete_csv_row, get_next_id
from utils.time_utils import get_timestamp
from users.models import User, get_user_by_id, get_user_by_username, get_user_by_email
import os


def create_user_admin(username, email, role):
    """
    Admin function to create new user with any role
    Adds to scns_users.csv with original format
    """
    # Validate role
    valid_roles = ['admin', 'faculty', 'student', 'visitor', 'staff']
    if role not in valid_roles:
        return None, f"Invalid role. Must be one of: {', '.join(valid_roles)}"
    
    # Check if username or email already exists
    if get_user_by_username(username):
        return None, "Username already exists"
    if get_user_by_email(email):
        return None, "Email already exists"
    
    # Get next ID
    next_id = get_next_id(config.USERS_CSV)
    
    # Create user data - original CSV format
    user_data = {
        'id': str(next_id),
        'username': username,
        'email': email,
        'role': role
    }
    
    # Read existing users and append
    users = read_csv(config.USERS_CSV)
    users.append(user_data)
    
    # Use original fieldnames
    fieldnames = ['id', 'username', 'email', 'role']
    if write_csv(config.USERS_CSV, users, fieldnames):
        log_admin_action('CREATE_USER', f"Created user {username} with role {role}")
        return User(**user_data), None
    
    return None, "Failed to create user"


def delete_user(user_id, admin_user_id):
    """
    Admin function to delete user (GDPR compliance)
    """
    user = get_user_by_id(user_id)
    if not user:
        return False, "User not found"
    
    # Prevent self-deletion
    if str(user_id) == str(admin_user_id):
        return False, "Cannot delete your own account"
    
    if delete_csv_row(config.USERS_CSV, 'id', user_id):
        log_admin_action('DELETE_USER', f"Deleted user {user.username} (ID: {user_id})")
        return True, None
    
    return False, "Failed to delete user"


def update_user_role(user_id, new_role, admin_user_id):
    """
    Admin function to update user role
    """
    valid_roles = ['admin', 'faculty', 'student', 'visitor', 'staff']
    if new_role not in valid_roles:
        return False, f"Invalid role. Must be one of: {', '.join(valid_roles)}"
    
    user = get_user_by_id(user_id)
    if not user:
        return False, "User not found"
    
    old_role = user.role
    
    # Update user in CSV
    users = read_csv(config.USERS_CSV)
    for u in users:
        if str(u['id']) == str(user_id):
            u['role'] = new_role
            break
    
    fieldnames = ['id', 'username', 'email', 'role']
    if write_csv(config.USERS_CSV, users, fieldnames):
        log_admin_action('UPDATE_ROLE', f"Changed {user.username} role from {old_role} to {new_role}")
        return True, None
    
    return False, "Failed to update role"


def get_users_by_role(role):
    """
    Get all users with a specific role
    """
    users = read_csv(config.USERS_CSV)
    return [User(**u) for u in users if u.get('role', '').lower() == role.lower()]


def get_user_stats():
    """
    Get user statistics by role
    Note: 'staff' in CSV is treated as 'faculty'
    """
    users = read_csv(config.USERS_CSV)
    stats = {
        'total': len(users),
        'admin': 0,
        'faculty': 0,  # This will include both 'faculty' and 'staff'
        'student': 0,
        'visitor': 0
    }
    
    for user in users:
        role = user.get('role', '').lower()
        if role == 'admin':
            stats['admin'] += 1
        elif role in ['faculty', 'staff']:  # Count staff as faculty
            stats['faculty'] += 1
        elif role == 'student':
            stats['student'] += 1
        elif role == 'visitor':
            stats['visitor'] += 1
    
    return stats


def log_admin_action(action_type, description):
    """
    Log admin actions for audit trail
    """
    try:
        os.makedirs(config.LOGS_DIR, exist_ok=True)
        timestamp = get_timestamp()
        log_entry = f"[{timestamp}] {action_type}: {description}\n"
        
        with open(config.AUDIT_LOG, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Error writing to audit log: {e}")
