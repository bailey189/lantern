from flask import Blueprint

about_bp = Blueprint('about', __name__, url_prefix="/about")

@about_bp.route("/")
def about():
    return "About Page"