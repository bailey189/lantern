# app/models.py (compatible with refactored app/__init__.py)
from flask_sqlalchemy import SQLAlchemy
from app import db

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(80))
    device_type = db.Column(db.String(80))
    manufacturer = db.Column(db.String(120))
    ip_address = db.Column(db.String(15), unique=True)
    mac_address = db.Column(db.String(17))
    operating_system = db.Column(db.String(120))
    risk_level = db.Column(db.String(20))

    ports = db.relationship('Port', backref='device', lazy=True)
    web_vulns = db.relationship('WebVuln', backref='device', lazy=True)

class Port(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    port_number = db.Column(db.Integer)
    service = db.Column(db.String(80))
    version = db.Column(db.String(120))
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'))

class WebVuln(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    issue = db.Column(db.Text)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'))
