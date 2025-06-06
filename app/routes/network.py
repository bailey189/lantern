from flask import Blueprint, jsonify
from app.models import Device


network_bp = Blueprint('network', __name__, url_prefix="/network")

@network_bp.route("/")
def network():
    return "Network Page"

@network_bp.route('/api/network')
def get_network_graph():
    devices = Device.query.all()
    nodes = [
        {"id": d.id, "label": f"{d.hostname or 'Unknown'}\n{d.ip_address}"}
        for d in devices
    ]

    # Placeholder: Add logic here to establish edges if known
    edges = []

    return jsonify({"nodes": nodes, "edges": edges})