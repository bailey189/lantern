from flask import Blueprint

results_bp = Blueprint('results', __name__, url_prefix="/results")

@results_bp.route("/")
def results():
    return "Results Page"