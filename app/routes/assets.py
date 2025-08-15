#routes/assets.py
# Lantern - Asset Management Module
from flask import Blueprint, render_template, request, flash, jsonify
from app.models import Asset, Credential, AssetTier, DataClassification, Port
from app import db

assets_bp = Blueprint('assets', __name__, url_prefix="/assets")

@assets_bp.route("/")
def assets():
    assets_list = Asset.query.order_by(Asset.last_scanned_date.desc().nullslast()).all()
    return render_template('assets.html', title="Lantern - Assets", assets=assets_list)

@assets_bp.route('/credentials', methods=['GET', 'POST'])
def save_credentials():
    if request.method == 'POST':
        ip = request.form.get('ip')
        username = request.form.get('username')
        password = request.form.get('password')

        asset = Asset.query.filter_by(ip_address=ip).first()
        if asset:
            cred = Credential(asset_id=asset.id, username=username, password=password)
            db.session.add(cred)
            db.session.commit()
            flash("Credentials saved", "success")
        else:
            flash("Asset not found", "error")

    return render_template('asset_credentials.html')

@assets_bp.route('/tier/<asset_id>')
def asset_tier_info(asset_id):
    asset = Asset.query.filter_by(id=asset_id).first()
    tier = asset.tier if asset and hasattr(asset, 'tier') else None
    return jsonify({
        "asset_name": asset.name if asset else "",
        "ip_address": asset.ip_address if asset else "",
        "tier_name": tier.name if tier else "",
        "tier_description": tier.description if tier else ""
    })

@assets_bp.route('/classification/<asset_id>')
def asset_classification_info(asset_id):
    asset = Asset.query.filter_by(id=asset_id).first()
    classification = asset.data_classification if asset and hasattr(asset, 'data_classification') else None
    return jsonify({
        "asset_name": asset.name if asset else "",
        "ip_address": asset.ip_address if asset else "",
        "classification_name": classification.name if classification else "",
        "classification_description": classification.description if classification else ""
    })

@assets_bp.route('/credentials/<asset_id>', methods=['GET', 'POST'])
def asset_credentials_info(asset_id):
    asset = Asset.query.filter_by(id=asset_id).first()
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        if asset:
            cred = Credential.query.filter_by(asset_id=asset.id).first()
            if not cred:
                cred = Credential(asset_id=asset.id)
                db.session.add(cred)
            cred.username = username
            cred.password = password  # Will be encrypted by the model property
            db.session.commit()
            return jsonify({"message": "Credentials saved."})
        return jsonify({"message": "Asset not found."}), 404

    credentials = []
    if asset and hasattr(asset, 'credentials'):
        for cred in asset.credentials:
            credentials.append({
                "username": cred.username,
                "password": "********"
            })
    return jsonify({
        "asset_name": asset.name if asset else "",
        "ip_address": asset.ip_address if asset else "",
        "credentials": credentials
    })

@assets_bp.route('/ports/<asset_id>')
def asset_ports_info(asset_id):
    asset = Asset.query.filter_by(id=asset_id).first()
    ports = []
    if asset and hasattr(asset, 'ports'):
        for port in asset.ports:
            ports.append({
                "port_number": port.port_number,
                "protocol": port.protocol,
                "service_name": port.service_name,
                "state": port.state
            })
    return jsonify({
        "asset_name": asset.name if asset else "",
        "ip_address": asset.ip_address if asset else "",
        "ports": ports
    })

@assets_bp.route('/info/<uuid:asset_id>')
def asset_full_info(asset_id):
    # asset_id will be a UUID object
    asset = Asset.query.filter_by(id=asset_id).first()
    if not asset:
        return jsonify({"error": "Asset not found"}), 404

    # Asset info
    asset_info = {
        "name": asset.name,
        "os_type": asset.os_type,
        "os_version": asset.os_version,
        "last_scanned_date": asset.last_scanned_date.strftime("%Y-%m-%d %H:%M:%S") if asset.last_scanned_date else None,
        "ip_address": asset.ip_address,
        "mac_address": getattr(asset, "mac_address", None)
    }

    # Credentials (show only one, or all if you prefer)
    credentials = []
    if hasattr(asset, 'credentials'):
        for cred in asset.credentials:
            credentials.append({
                "username": cred.username,
                "password": "********"  # Masked for security
            })

    # Network ports
    ports = []
    if hasattr(asset, 'ports'):
        for port in asset.ports:
            ports.append({
                "port_number": port.port_number,
                "protocol": port.protocol,
                "service_name": port.service_name,
                "state": port.state
            })

    return jsonify({
        "asset_info": asset_info,
        "credentials": credentials,
        "ports": ports
    })
