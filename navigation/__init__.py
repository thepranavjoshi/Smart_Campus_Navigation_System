# Navigation package
from flask import Blueprint

navigation_bp = Blueprint('navigation', __name__, url_prefix='/navigation')

from navigation import routes
