from flask import Blueprint

settings_bp = Blueprint('settings', __name__, url_prefix="/settings")

@settings_bp.route("/")
def settings():
    return "Settings Page"