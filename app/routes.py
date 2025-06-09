from flask import Blueprint, render_template, request, redirect, url_for, flash
import subprocess

bp = Blueprint('main', __name__)

# Home Redirect
@bp.route('/')
def index():
    return render_template('index.html')

# Scan Page
@bp.route('/scan', methods=['GET', 'POST'])
def scan():
    result = None
    if request.method == 'POST':
        target = request.form.get('target', '192.168.1.0/24')
        try:
            result = subprocess.check_output(['nmap', '-sn', target], text=True)
            flash('Scan completed successfully.', 'success')
        except subprocess.CalledProcessError as e:
            result = f"Scan failed: {e}"
            flash('Scan failed.', 'danger')
    return render_template('scan.html', result=result)

# Network Page
@bp.route('/network')
def network():
    # This page should later use data from the DB to generate a topology graph
    return render_template('network.html')

# Devices Page
@bp.route('/devices')
def devices():
    # This page should later show a table of discovered devices
    return render_template('devices.html')

# Results Page
@bp.route('/results')
def results():
    # This page could show historical scan results
    return render_template('results.html')

# Settings Page
@bp.route('/settings', methods=['GET', 'POST'])
def settings():
    # Future: allow configuration of scanning settings or service parameters
    if request.method == 'POST':
        flash('Settings saved (placeholder).', 'success')
        return redirect(url_for('main.settings'))
    return render_template('settings.html')

# About Page
@bp.route('/about')
def about():
    return render_template('about.html')
