import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = 'postgresql://lanternuser:64B6/0j+m]BX-HI[C}vSq+U@localhost:5432/lanterndb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
