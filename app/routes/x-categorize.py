from flask import Blueprint

categorize_bp = Blueprint("categorize", __name__, url_prefix="/categorize")

@categorize_bp.route("/", methods=["POST"])
def categorize():
    return {"status": "categorize placeholder"}