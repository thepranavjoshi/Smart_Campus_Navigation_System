"""
Setup Script - Initialize test users with passwords
Run this once to set up the test accounts
"""
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.hashing import hash_password
from utils.csv_handler import write_csv
import config

def setup_test_users():
    """
    Create test users with proper password hashes
    """
    users = [
        {
            'id': '1',
            'username': 'admin',
            'email': 'admin@stmarys.com',
            'role': 'admin',
            'password_hash': hash_password('admin123'),
            'consent': 'True',
            'mfa_secret': ''
        },
        {
            'id': '2',
            'username': 'faculty',
            'email': 'faculty@stmarys.com',
            'role': 'faculty',
            'password_hash': hash_password('faculty123'),
            'consent': 'True',
            'mfa_secret': ''
        },
        {
            'id': '3',
            'username': 'student',
            'email': 'student@stmarys.com',
            'role': 'student',
            'password_hash': hash_password('student123'),
            'consent': 'True',
            'mfa_secret': ''
        },
        {
            'id': '4',
            'username': 'visitor',
            'email': 'visitor@stmarys.com',
            'role': 'visitor',
            'password_hash': hash_password('visitor123'),
            'consent': 'True',
            'mfa_secret': ''
        }
    ]
    
    fieldnames = ['id', 'username', 'email', 'role', 'password_hash', 'consent', 'mfa_secret']
    
    if write_csv(config.USERS_CSV, users, fieldnames):
        print("Test users created successfully!")
        print("\nTest Accounts:")
        print("-" * 40)
        print("Username    | Password    | Role")
        print("-" * 40)
        print("admin       | admin123    | Administrator")
        print("faculty     | faculty123  | Faculty")
        print("student     | student123  | Student")
        print("visitor     | visitor123  | Visitor")
        print("-" * 40)
        return True
    else:
        print("Failed to create test users!")
        return False

if __name__ == '__main__':
    setup_test_users()
