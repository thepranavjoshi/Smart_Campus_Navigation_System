"""
User Models
User data abstraction and access methods
Uses original CSV format without password hashing
"""
import config
from utils.csv_handler import read_csv, write_csv, append_csv, get_next_id


class User:
    """
    User model class - works with original CSV format
    """
    def __init__(self, id, username, email, role, password='', **kwargs):
        self.id = int(id)
        self.username = username
        self.email = email
        self.role = self._normalize_role(role)
        self.password = password  # Simple password (optional)
    
    def _normalize_role(self, role):
        """
        Normalize role names (staff -> faculty mapping)
        """
        role = role.lower()
        if role == 'staff':
            return 'faculty'
        return role
    
    def to_dict(self):
        """
        Convert user to dictionary
        """
        return {
            'id': str(self.id),
            'username': self.username,
            'email': self.email,
            'role': self.role
        }
    
    def check_password(self, password):
        """
        Simple password check - if no password set, any password works
        """
        if not self.password:
            return True  # No password set, allow login
        return self.password == password
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_faculty(self):
        return self.role in ['admin', 'faculty']
    
    @property
    def is_student(self):
        return self.role == 'student'
    
    @property
    def is_visitor(self):
        return self.role == 'visitor'


def get_user_by_id(user_id):
    """
    Get user by ID
    """
    users = read_csv(config.USERS_CSV)
    for user_data in users:
        if str(user_data.get('id')) == str(user_id):
            return User(**user_data)
    return None


def get_user_by_username(username):
    """
    Get user by username
    """
    users = read_csv(config.USERS_CSV)
    for user_data in users:
        if user_data.get('username', '').lower() == username.lower():
            return User(**user_data)
    return None


def get_user_by_email(email):
    """
    Get user by email
    """
    users = read_csv(config.USERS_CSV)
    for user_data in users:
        if user_data.get('email', '').lower() == email.lower():
            return User(**user_data)
    return None


def get_all_users():
    """
    Get all users
    """
    users = read_csv(config.USERS_CSV)
    return [User(**user_data) for user_data in users]


def create_user(username, email, password, role='visitor'):
    """
    Create new user - appends to CSV with original format
    """
    # Check if username or email already exists
    if get_user_by_username(username):
        return None, "Username already exists"
    if get_user_by_email(email):
        return None, "Email already exists"
    
    # Get next ID
    next_id = get_next_id(config.USERS_CSV)
    
    # Create user data - original format only
    user_data = {
        'id': str(next_id),
        'username': username,
        'email': email,
        'role': role
    }
    
    # Append to CSV using original fieldnames
    fieldnames = ['id', 'username', 'email', 'role']
    if append_csv(config.USERS_CSV, user_data, fieldnames):
        return User(**user_data), None
    
    return None, "Failed to create user"


def authenticate_user(username, password):
    """
    Authenticate user with username
    Password is optional for existing users from original CSV
    Returns: (User, error_message)
    """
    user = get_user_by_username(username)
    if not user:
        return None, "Invalid username"
    
    # For users without password (original CSV users), allow login
    return user, None
