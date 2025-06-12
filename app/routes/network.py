# app/routes/network.py
from flask import Blueprint, render_template, jsonify
from app.models import Asset

network_bp = Blueprint('network_bp', __name__, url_prefix='/network')

@network_bp.route('/')
def network():
    return render_template('network.html')

@network_bp.route('/data')
def network_data():
    assets = Asset.query.all()
    nodes = []
    edges = []

    # Add each asset as a node
    for asset in assets:
        nodes.append({
            "id": str(asset.id),
            "label": asset.name or asset.ip_address,
            "title": f"IP: {asset.ip_address}<br>OS: {asset.os_type or 'Unknown'}"
        })

    # If you have no route info, don't add edges, or add a dummy edge if you want to show something
    # Optionally, you can connect all nodes to a "network" node for visualization
    if len(nodes) > 1:
        network_node = {"id": "network", "label": "Network", "color": "#cccccc"}
        nodes.append(network_node)
        for node in nodes:
            if node["id"] != "network":
                edges.append({"from": "network", "to": node["id"]})

    return jsonify({"nodes": nodes, "edges": edges})
