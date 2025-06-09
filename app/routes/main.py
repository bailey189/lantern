from flask import Blueprint, render_template

# Create a Blueprint named 'main_bp'
main_bp = Blueprint('main_bp', __name__)

# Define the root route for this blueprint
@main_bp.route('/')
def index():
    """
    Renders the main homepage of the application.
    This function will be executed when a GET request is made to the root URL (/).
    It will look for an 'index.html' file inside the 'templates' folder.
    """
    return render_template('index.html')

# You can add other routes specific to your main or general pages here
# For example:
# @main_bp.route('/contact')
# def contact():
#     return "Contact Us Page"

