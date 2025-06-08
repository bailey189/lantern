from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

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
    from app.routes.scan import scan_bp
    from app.routes.network import network_bp
    from app.routes.devices import devices_bp
    from app.routes.results import results_bp
    from app.routes.settings import settings_bp
    from app.routes.about import about_bp

    app.register_blueprint(scan_bp)
    app.register_blueprint(network_bp)
    app.register_blueprint(devices_bp)
    app.register_blueprint(results_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(about_bp)

    # Optional: example route to list all registered routes (debugging)
    @app.route('/routes')
    def list_routes():
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(f"{rule.endpoint}: {rule}")
        return "<br>".join(sorted(routes))

    return app
