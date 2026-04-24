import os

# Base directory paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')
TEMPLATE_FOLDER = FRONTEND_DIR
STATIC_FOLDER = os.path.join(FRONTEND_DIR, 'static')
UPLOAD_FOLDER = os.path.join(STATIC_FOLDER, 'uploads')

class Config:
    SECRET_KEY = 'your_secret_key_here'
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024 # 2MB limit
    UPLOAD_FOLDER = UPLOAD_FOLDER
    
    # Mail settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'shafraan95@gmail.com'
    MAIL_PASSWORD = 'kxkzdwsbvbojnwqs'

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',      # Default XAMPP user
    'password': '',      # Default XAMPP password (empty)
    'database': 'matching'
}
