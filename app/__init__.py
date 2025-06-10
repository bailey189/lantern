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
    # Note: The order of blueprint registration doesn't strictly matter for functionality,
    # but placing the 'main' blueprint first can sometimes make sense for clarity
    # if it's considered the primary entry point.
    from app.routes.index import index_bp 
    from app.routes.scan import scan_bp 
    from app.routes.network import network_bp 
    from app.routes.assets import assets_bp 
    from app.routes.results import results_bp 
    from app.routes.settings import settings_bp 
    from app.routes.about import about_bp 
    
    app.register_blueprint(index_bp) 
    app.register_blueprint(scan_bp )
    app.register_blueprint(network_bp )
    app.register_blueprint(assets_bp )
    app.register_blueprint(results_bp)
    app.register_blueprint(settings_bp )
    app.register_blueprint(about_bp )

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

    return app

