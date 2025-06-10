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
    from app.routes.scan import scan
    from app.routes.network import network
    from app.routes.devices import devices
    from app.routes.results import results
    from app.routes.settings import settings
    from app.routes.about import about
    
    app.register_blueprint(index_bp) 
    app.register_blueprint(scan)
    app.register_blueprint(network)
    app.register_blueprint(devices)
    app.register_blueprint(results)
    app.register_blueprint(settings)
    app.register_blueprint(about)

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

