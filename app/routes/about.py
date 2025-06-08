from flask import Blueprint, render_template

about_bp = Blueprint('about', __name__, url_prefix='/about')

@about_bp.route('/')
def about_home():
    return render_template('about.html', title="About Lantern")
