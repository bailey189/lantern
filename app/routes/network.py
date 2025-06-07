# app/routes/network.py
from flask import Blueprint, render_template, jsonify
from app.models import Device, Port

network_bp = Blueprint('network', __name__, url_prefix='/network')

@network_bp.route('/')
def network():
    return render_template('network.html')

@network_bp.route('/data')
def network_data():
    devices = Device.query.all()
    nodes = []
    edges = []

    for device in devices:
        nodes.append({"id": device.id, "label": device.hostname or device.ip_address})

    for device in devices:
        for port in device.ports:
            # Add a dummy edge to show communication (could be refined with scan data)
            edges.append({"from": device.id, "to": device.id, "label": f"Port {port.port_number}"})

    return jsonify({"nodes": nodes, "edges": edges})
