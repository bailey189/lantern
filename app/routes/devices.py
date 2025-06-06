from flask import Blueprint

devices_bp = Blueprint('devices', __name__, url_prefix="/devices")

@devices_bp.route("/")
def devices():
    return "Devices Page"