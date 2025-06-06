from flask import Blueprint

scan_bp = Blueprint('scan', __name__, url_prefix="/scan")

@scan_bp.route("/")
def scan():
    return "Scan Page"