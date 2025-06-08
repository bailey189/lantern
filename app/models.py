# app/models.py
from app import db
from datetime import datetime


    
class Scan(db.Model):
    __tablename__ = 'scans'
    id = db.Column(db.Integer, primary_key=True)
    tool_name = db.Column(db.String(64), nullable=False)
    target = db.Column(db.String(256), nullable=True)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime, nullable=True)
    
    results = db.relationship('ScanResult', backref='scan', lazy=True)

class ScanResult(db.Model):
    __tablename__ = 'scan_results'
    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scans.id'), nullable=False)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=True)
    output = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Device(db.Model):
    __tablename__ = 'devices'

    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), unique=True, nullable=False)
    mac_address = db.Column(db.String(17))
    hostname = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime)
    
    # Add this:
    credentials = db.relationship('Credential', back_populates='device', cascade="all, delete-orphan")
    
class Credential(db.Model):
    __tablename__ = 'credentials'

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)
    username = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(128), nullable=False)  # Consider encryption for production
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    device = db.relationship('Device', back_populates='credentials')
    
class Port(db.Model):
    __tablename__ = 'ports'
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)
    port_number = db.Column(db.Integer, nullable=False)
    protocol = db.Column(db.String(10), nullable=False)  # e.g. tcp, udp
    service_name = db.Column(db.String(128), nullable=True)
    state = db.Column(db.String(64), nullable=True)  # open, closed, filtered, etc.

class Vulnerability(db.Model):
    __tablename__ = 'vulnerabilities'
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)
    scan_result_id = db.Column(db.Integer, db.ForeignKey('scan_results.id'), nullable=True)
    cve_id = db.Column(db.String(50), nullable=True)  # CVE identifier if applicable
    description = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(32), nullable=True)  # e.g. low, medium, high, critical
    found_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    scan_result = db.relationship('ScanResult', backref=db.backref('vulnerabilities', lazy=True))

class Route(db.Model):
    __tablename__ = 'routes'
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)
    destination = db.Column(db.String(45), nullable=False)  # destination IP or subnet
    gateway = db.Column(db.String(45), nullable=False)  # gateway IP
    interface = db.Column(db.String(64), nullable=True)
    metric = db.Column(db.Integer, nullable=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    device = db.relationship('Device', backref=db.backref('routes', lazy=True))
