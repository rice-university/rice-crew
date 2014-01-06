import os
from pytz import timezone

DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///sqlite.db')
SECRET_KEY = os.environ['SECRET_KEY']
ALLOWED_HOSTS = os.environ['ALLOWED_HOSTS'].split(',')

TIMEZONE = timezone('America/Chicago')

# username to (is_admin, password) map for the super legit authenticaion system
USERS = {
    os.environ['STANDARD_USER']: (False, os.environ['STANDARD_PASS']),
    os.environ['ADMIN_USER']: (True, os.environ['ADMIN_PASS'])
}
