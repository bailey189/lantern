from flask import Blueprint, render_template, redirect, url_for, request, flash

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def index():
    # Logic to determine what the first button should say
    # For now, always "Initial Survey"
    survey_button_text = "Initial Survey"
    return render_template('index.html', survey_button_text=survey_button_text)

@main_bp.route('/survey', methods=['POST'])
def survey():
    # Placeholder for survey logic
    flash("Survey started (not implemented).")
    return redirect(url_for('main.index'))

@main_bp.route('/generate_report', methods=['POST'])
def generate_report():
    # Placeholder for report generation logic
    flash("Report generation started (not implemented).")
    return redirect(url_for('main.index'))

@main_bp.route('/wipe_system', methods=['POST'])
def wipe_system():
    # Placeholder for wipe logic
    flash("System wipe started (not implemented).")
    return redirect(url_for('main.index'))