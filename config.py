import os

# Flask Configuration
SECRET_KEY = 'scns-flask-secret-key-2024-secure'

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data paths
DATA_DIR = os.path.join(BASE_DIR, 'data')
USERS_CSV = os.path.join(DATA_DIR, 'scns_users.csv')
LOCATIONS_CSV = os.path.join(DATA_DIR, 'scns_locations.csv')
ROUTES_CSV = os.path.join(DATA_DIR, 'scns_routes.csv')
NOTIFICATIONS_CSV = os.path.join(DATA_DIR, 'scns_notifications.csv')

# Logs directory
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
ACTIVITY_LOG = os.path.join(LOGS_DIR, 'activity_log.txt')
ALERTS_LOG = os.path.join(LOGS_DIR, 'alerts_log.txt')
AUDIT_LOG = os.path.join(LOGS_DIR, 'audit_log.txt')

# Static and Templates
STATIC_DIR = os.path.join(BASE_DIR, 'static')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

# Session configuration
SESSION_TYPE = 'filesystem'
PERMANENT_SESSION_LIFETIME = 3600  # 1 hour

# MFA Configuration
MFA_OTP_VALIDITY = 300  # 5 minutes in seconds
