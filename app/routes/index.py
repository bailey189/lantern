# app/routes/index.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from app.models import SurveyResult
from app import db
import subprocess
import os
import sys
from app.utils.network import get_host_network
from app.models import Port, ScanResult, Scan, Asset, Vulnerability

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

@index_bp.route('/license')
def license():
    return render_template('license.html')

@index_bp.route('/network', methods=['POST', 'GET'])
def network():
    # Your logic here
    return render_template('network.html')

@index_bp.route('/report', methods=['GET', 'POST'])
def report():
    # Gather all data needed for the report
    assets = Asset.query.all()
    scans = Scan.query.order_by(Scan.started_at.desc()).all()
    vulnerabilities = Vulnerability.query.all()  # Example model
    recommendations = []  # Generate or fetch recommendations

    return render_template(
        'report.html',
        assets=assets,
        scans=scans,
        vulnerabilities=vulnerabilities,
        recommendations=recommendations
    )

@index_bp.route('/run_update', methods=['POST'])
def run_update():
    progress_file = "update_progress.txt"
    # Remove old progress file if it exists
    if os.path.exists(progress_file):
        os.remove(progress_file)
    with open(progress_file, "w") as f:
        f.write("Starting Lantern update...\n")
    # Open the file in append mode for the subprocess
    with open(progress_file, "a") as out:
        # Use close_fds=True to avoid leaking file descriptors
        subprocess.Popen(
            ['bash', 'update_lantern.sh'],
            stdout=out,
            stderr=subprocess.STDOUT,
            close_fds=True
        )
    flash("Lantern update script started. The page will refresh in 30 seconds.", "success")
    return render_template('update_wait.html')

@index_bp.route('/scans')
def scans():
    nmap_subnet = get_host_network()
    return render_template('scans.html', nmap_subnet=nmap_subnet)

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
        # Delete all records from the tables
        db.session.query(Port).delete()
        db.session.query(ScanResult).delete()
        db.session.query(Scan).delete()
        db.session.query(Asset).delete()
        db.session.commit()
        flash("All system data has been wiped from Port, ScanResult, Scan, and Asset tables.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"System wipe failed: {e}", "danger")
    return redirect(url_for('index_bp.index'))
