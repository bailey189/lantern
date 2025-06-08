from flask import Blueprint

devices_bp = Blueprint('devices', __name__, url_prefix="/devices")

@devices_bp.route("/")
def devices():
    return "Devices Page"

@devices_bp.route('/credentials', methods=['GET', 'POST'])
def save_credentials():
    if request.method == 'POST':
        ip = request.form.get('ip')
        username = request.form.get('username')
        password = request.form.get('password')

        device = Device.query.filter_by(ip_address=ip).first()
        if device:
            cred = Credential(device_id=device.id, username=username, password=password)
            db.session.add(cred)
            db.session.commit()
            flash("Credentials saved", "success")
        else:
            flash("Device not found", "error")

    return render_template('device_credentials.html')
