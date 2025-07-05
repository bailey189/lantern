# config.py
import os
import logging

FERNET_KEY = os.environ.get("FERNET_KEY")

class Config:
    # General Config
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-default-secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Database Config
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://lanternuser:64B6/0j+m]BX-HI[C}vSq+U@localhost:5432/lanterndb'
    )

    # Logging configuration
    LOG_FILE = 'lantern_debug.log'
    LOG_LEVEL = logging.DEBUG  # Change to logging.INFO or logging.ERROR for production

    @staticmethod
    def init_app(app):
        # Remove any existing handlers
        for handler in app.logger.handlers[:]:
            app.logger.removeHandler(handler)

        # Set up file handler
        file_handler = logging.FileHandler(Config.LOG_FILE)
        file_handler.setLevel(Config.LOG_LEVEL)
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        )
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(Config.LOG_LEVEL)

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False


