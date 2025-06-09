# app/routes/network.py
from flask import Blueprint, render_template, jsonify
from app.models import Asset, Port

network_bp = Blueprint('network', __name__, url_prefix='/network')

@network_bp.route('/')
def network():
    return render_template('network.html')

@network_bp.route('/data')
def network_data():
    assets = Asset.query.all()
    nodes = []
    edges = []

    for asset in assets:
        nodes.append({"id": asset.id, "label": asset.hostname or asset.ip_address})

    for asset in assets:
        for port in asset.ports:
            # Add a dummy edge to show communication (could be refined with scan data)
            edges.append({"from": asset.id, "to": asset.id, "label": f"Port {port.port_number}"})

    return jsonify({"nodes": nodes, "edges": edges})
