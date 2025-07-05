# app/routes/index.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from app.models import SurveyResult
from app import db
import subprocess
import os
import sys

# Your blueprint is named 'index_bp'
index_bp = Blueprint('index_bp', __name__) # IMPORTANT: Ensure this is 'index_bp' if you also had 'index' previously

UPDATE_PROGRESS_FILE = "update_progress.txt"

@index_bp.route('/', methods=['GET'])
def index():
    button_text = "Initial Survey"
    return render_template('index.html', action_button_text=button_text)

@index_bp.route('/about')
def about():
    debug_log = None
    if current_app.logger.level == 10:  # logging.DEBUG == 10
        try:
            with open('lantern_debug.log', 'r') as f:
                debug_log = f.read()[-10000:]  # Show last 10,000 chars
        except Exception:
            debug_log = "Debug log file not found."
    return render_template('about.html', debug_log=debug_log)

@index_bp.route('/network', methods=['POST', 'GET'])
def network():
    # Your logic here
    return render_template('network.html')

@index_bp.route('/report', methods=['GET', 'POST'])
def report():
    # Your report logic here
    return render_template('report.html')

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

@index_bp.route('/scans')
def scans():
    return render_template('scans.html')

@index_bp.route('/survey', methods=['GET', 'POST'])
def survey():
    if request.method == 'POST':
        # Collect form data
        data = request.form
        survey = SurveyResult(
            business_name=data.get('business_name'),
            naics_code=data.get('naics_code'),
            glba=data.get('glba'),
            hipaa=data.get('hipaa'),
            coppa=data.get('coppa'),
            fisma=data.get('fisma'),
            cmmc=data.get('cmmc'),
            ferpa=data.get('ferpa'),
            state_privacy_laws=data.get('state_privacy_laws'),
            pci=data.get('pci'),
            soc2=data.get('soc2'),
            iso=data.get('iso'),
            csf=data.get('csf'),
            nist_80053=data.get('nist_80053'),
            nist_800171=data.get('nist_800171'),
            cis=data.get('cis'),
        )
        db.session.add(survey)
        db.session.commit()
        flash("Thank you for submitting the survey!", "success")
        return redirect(url_for('index_bp.index'))
    return render_template('survey.html')

@index_bp.route('/update_progress')
def update_progress():
    if os.path.exists(UPDATE_PROGRESS_FILE):
        with open(UPDATE_PROGRESS_FILE) as f:
            progress = f.read()
    else:
        progress = "No update in progress."
    return progress, 200, {'Content-Type': 'text/plain'}


@index_bp.route('/wipe_system', methods=['POST'])
def wipe_system():
    try:
        # Run the Database_reset.py script located in /standalone
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'standalone', 'Database_reset.py')
        subprocess.run([sys.executable, script_path], check=True)
        flash("System wipe completed successfully.", "success")
    except Exception as e:
        flash(f"System wipe failed: {e}", "danger")
    return redirect(url_for('index_bp.index'))
