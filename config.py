# config.py
import os
FERNET_KEY = os.environ.get("FERNET_KEY")

class Config:
    # General Config
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-default-secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Database Config
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://lanternuser:64B6/0j+m]BX-HI[C}vSq+U@localhost:5432/lanterndb'
    )
class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False


