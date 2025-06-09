from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
#from app.routes.index import index_bp

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Load configuration from config.py
    app.config.from_object('config.Config')
    
    # Initialize database and migrations
    db.init_app(app)
    migrate.init_app(app, db)

    # Import and register blueprints
    from app.routes.index import index_bp
    from app.routes.scan import scan_bp
    from app.routes.network import network_bp
    from app.routes.devices import devices_bp
    from app.routes.results import results_bp
    from app.routes.settings import settings_bp
    from app.routes.about import about_bp

    app.register_blueprint(index_bp)
    app.register_blueprint(scan_bp)
    app.register_blueprint(network_bp)
    app.register_blueprint(devices_bp)
    app.register_blueprint(results_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(about_bp)

    return app
