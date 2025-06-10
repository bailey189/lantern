from flask import Blueprint, render_template

assets_bp = Blueprint('assets', __name__, url_prefix="/assets")

@assets_bp.route("/")
def assets():
        return render_template('assets.html', title="Lantern - Assets")

@assets_bp.route('/credentials', methods=['GET', 'POST'])
def save_credentials():
    if request.method == 'POST':
        ip = request.form.get('ip')
        username = request.form.get('username')
        password = request.form.get('password')

        asset = asset.query.filter_by(ip_address=ip).first()
        if asset:
            cred = Credential(asset_id=asset.id, username=username, password=password)
            db.session.add(cred)
            db.session.commit()
            flash("Credentials saved", "success")
        else:
            flash("asset not found", "error")

    return render_template('asset_credentials.html')
