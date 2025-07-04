# app/routes/index.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
import subprocess
import os

# Your blueprint is named 'index_bp'
index_bp = Blueprint('index_bp', __name__) # IMPORTANT: Ensure this is 'index_bp' if you also had 'index' previously

UPDATE_PROGRESS_FILE = "update_progress.txt"

@index_bp.route('/', methods=['GET'])
def index():
    action_button_text = "Initial Survey"
    return render_template('index.html', action_button_text=action_button_text)

@index_bp.route('/survey', methods=['GET', 'POST'])
def survey():
    if request.method == 'POST':
        flash("Thank you for submitting the survey!", "success")
        return redirect(url_for('index_bp.index'))
    return render_template('survey.html')

@index_bp.route('/generate_report', methods=['POST'])
def generate_report():
    flash("Report generation started (not implemented).")
    return redirect(url_for('index_bp.index'))

@index_bp.route('/wipe_system', methods=['POST'])
def wipe_system():
    flash("System wipe started (not implemented).")
    return redirect(url_for('index_bp.index'))

@index_bp.route('/run_update', methods=['POST'])
def run_update():
    # Remove old progress file if it exists
    if os.path.exists(UPDATE_PROGRESS_FILE):
        os.remove(UPDATE_PROGRESS_FILE)
    # Start the update script and redirect to wait page
    with open(UPDATE_PROGRESS_FILE, "w") as f:
        f.write("Starting Lantern update...\n")
    # Run the update script and redirect output to the progress file
    subprocess.Popen(
        ['bash', 'update_lantern.sh'],
        stdout=open(UPDATE_PROGRESS_FILE, "a"),
        stderr=subprocess.STDOUT
    )
    flash("Lantern update script started. The page will refresh in 30 seconds.", "success")
    return render_template('update_wait.html')

@index_bp.route('/update_progress')
def update_progress():
    if os.path.exists(UPDATE_PROGRESS_FILE):
        with open(UPDATE_PROGRESS_FILE) as f:
            progress = f.read()
    else:
        progress = "No update in progress."
    return progress, 200, {'Content-Type': 'text/plain'}

@index_bp.route('/about')
def about():
    return render_template('about.html') 