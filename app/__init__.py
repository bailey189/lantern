from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

from cryptography.fernet import Fernet
os.environ["FERNET_KEY"] = Fernet.generate_key().decode()


db = SQLAlchemy()
migrate = Migrate()

def create_app(config_object='config.Config'):
    app = Flask(__name__)
    
    # Load configuration from the config object
    app.config.from_object(config_object)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Import and register blueprints
    from app.routes.index import index_bp 
    from app.routes.scan import scan_bp 
    from app.routes.network import network_bp 
    from app.routes.assets import assets_bp 
    from app.routes.results import results_bp 
    from app.routes.settings import settings_bp 
    from app.routes.about import about_bp 
    from app.routes.main import main_bp 
    
    app.register_blueprint(index_bp) 
    app.register_blueprint(scan_bp )
    app.register_blueprint(network_bp )
    app.register_blueprint(assets_bp )
    app.register_blueprint(results_bp)
    app.register_blueprint(settings_bp )
    app.register_blueprint(about_bp )
    app.register_blueprint(main_bp)

    # Optional: example route to list all registered routes (debugging)
    @app.route('/routes')
    def list_routes():
        """
        Debugging utility route to list all registered routes in the application.
        Useful for verifying that all blueprints and their routes are loaded correctly.
        """
        routes = []
        for rule in app.url_map.iter_rules():
            methods = ','.join(rule.methods - set(['HEAD', 'OPTIONS']))
            routes.append(f"{rule.endpoint}: {rule.rule} [{methods}]")
        return "<br>".join(sorted(routes))

    # --- CLI command to populate AssetTier table ---
    @app.cli.command("populate-assettier")
    def populate_assettier():
        """Populate the AssetTier table with default records."""
        from app.models import AssetTier
        tiers = [
            {"name": "Mission-Critical", "description": "Essential systems for business continuity (e.g., payroll, authentication servers)."},
            {"name": "Business-Critical", "description": "Important systems supporting operations but not catastrophic if unavailable (e.g., CRM, inventory management)."},
            {"name": "Operational Support", "description": "Devices that improve efficiency but do not directly impact core business functions (e.g., workstations, internal file servers)."},
            {"name": "Non-Critical", "description": "Convenience-based or auxiliary systems with minimal impact (e.g., newsletter servers, guest Wi-Fi)."}
        ]
        from app import db
        for tier in tiers:
            if not AssetTier.query.filter_by(name=tier["name"]).first():
                db.session.add(AssetTier(name=tier["name"], description=tier["description"]))
        db.session.commit()
        print("AssetTier table populated.")

    return app

