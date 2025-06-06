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