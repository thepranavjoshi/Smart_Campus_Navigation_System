"""
Password Hashing Utility
Secure password hashing using hashlib
"""
import hashlib
import secrets


def generate_salt():
    """
    Generate a random salt for password hashing
    """
    return secrets.token_hex(16)


def hash_password(password, salt=None):
    """
    Hash password using SHA256 with salt
    Returns: tuple (hash, salt)
    """
    if salt is None:
        salt = generate_salt()
    
    # Combine password and salt
    salted = (password + salt).encode('utf-8')
    
    # Create SHA256 hash
    hashed = hashlib.sha256(salted).hexdigest()
    
    # Return combined hash:salt format
    return f"{hashed}:{salt}"


def verify_password(password, stored_hash):
    """
    Verify password against stored hash
    Returns: True if password matches, False otherwise
    """
    try:
        if ':' not in stored_hash:
            return False
        
        # Extract salt from stored hash
        hashed, salt = stored_hash.rsplit(':', 1)
        
        # Hash the input password with the same salt
        salted = (password + salt).encode('utf-8')
        check_hash = hashlib.sha256(salted).hexdigest()
        
        return check_hash == hashed
    except Exception:
        return False


def generate_temp_password():
    """
    Generate a temporary password for new users
    """
    return secrets.token_urlsafe(12)
