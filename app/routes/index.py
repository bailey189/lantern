# app/routes/index.py
from flask import Blueprint, render_template

# Your blueprint is named 'index_bp'
index_bp = Blueprint('index_bp', __name__) # IMPORTANT: Ensure this is 'index_bp' if you also had 'index' previously

@index_bp.route('/')
def index(): # CHANGED: Renamed 'home' to 'index' to match Flask's expectation
    """
    Handles requests to the root URL (/).
    Renders the 'index.html' template located in the 'app/templates/' directory.
    The 'title' variable is passed to the template for dynamic content.
    """
    return render_template('index.html', title="Lantern - Home")

