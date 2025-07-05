# app/routes/network.py
from flask import Blueprint, render_template, jsonify
from app.models import Asset, Route
import netifaces
import ipaddress

network_bp = Blueprint('network_bp', __name__, url_prefix='/network')

@network_bp.route('/')
def network():
    return render_template('network.html')

@network_bp.route('/data')
def network_data():
    assets = Asset.query.all()
    routes = Route.query.order_by(Route.hop_number).all()
    nodes = []
    edges = []

    asset_id_to_node = {}

    # Add each asset as a node
    for asset in assets:
        node = {
            "id": str(asset.id),
            "label": asset.name or asset.ip_address,
            "title": f"IP: {asset.ip_address}<br>OS: {asset.os_type or 'Unknown'}"
        }
        nodes.append(node)
        asset_id_to_node[str(asset.id)] = node

    # Add gateway nodes (hop_number == 0) and build edges for hops
    gateway_ips = set()
    for route in routes:
        if route.hop_number == 0:
            gateway_ips.add(str(route.hop_ip))

    # Add gateway nodes if not already present
    for gw_ip in gateway_ips:
        if not any(n["id"] == gw_ip for n in nodes):
            nodes.append({
                "id": gw_ip,
                "label": f"Gateway {gw_ip}",
                "color": "#cccccc",
                "title": f"Gateway IP: {gw_ip}"
            })

    # Build edges for each route (hop)
    for route in routes:
        # For hop_number 0, connect asset to gateway
        if route.hop_number == 0:
            edges.append({
                "from": str(route.asset_id),
                "to": str(route.hop_ip),
                "label": "gateway",
                "arrows": "to"
            })
        else:
            # For other hops, connect previous hop to this hop
            prev_hop = None
            # Find previous hop_ip for this asset
            prev_route = Route.query.filter_by(asset_id=route.asset_id, hop_number=route.hop_number - 1).first()
            if prev_route:
                prev_hop = str(prev_route.hop_ip)
            else:
                prev_hop = str(route.asset_id)
            edges.append({
                "from": prev_hop,
                "to": str(route.hop_ip),
                "label": f"hop {route.hop_number}",
                "arrows": "to"
            })

    return jsonify({"nodes": nodes, "edges": edges})

def get_host_network():
    """Return the host's primary subnet in CIDR notation, e.g., '192.168.1.0/24'."""
    try:
        gws = netifaces.gateways()
        default_iface = gws['default'][netifaces.AF_INET][1]
        iface_info = netifaces.ifaddresses(default_iface)[netifaces.AF_INET][0]
        ip = iface_info['addr']
        netmask = iface_info['netmask']
        network = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False)
        return str(network)
    except Exception as e:
        return None
