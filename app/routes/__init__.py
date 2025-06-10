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
    # Import your existing 'index_bp' for the homepage
    from app.routes.index import index_bp # IMPORTANT: Use your existing index.py blueprint
    from app.routes.scan import scan
    from app.routes.network import network
    from app.routes.assets import assets
    from app.routes.results import results
    from app.routes.settings import settings
    from app.routes.about import about

    # Register index_bp to handle the root URL
    app.register_blueprint(index_bp) 
    app.register_blueprint(scan)
    app.register_blueprint(network)
    aapp.register_blueprint(assets)
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

