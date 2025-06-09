# db_reset.py

from app import create_app, db
# Import all your models so SQLAlchemy knows about them
# from app.models import (
#     AssetTier, BusinessUnit, DataClassification, NetworkSegment, Team,
#     CVE, CWE, RemediationFix, ThreatIntelligence, RuleCVE, RuleCWE,
#     MisconfigThreatIntel, ThreatIntelligenceCVE, Scan, Asset, Credential,
#     Port, Route, InstalledApplication, SecurityControl, ScanResult,
#     MisconfigurationRule, AssetMisconfiguration, RemediationAction
# )
# A more robust way to ensure all models are imported:
# You can try importing the models module directly if structured well,
# or ensure `from app import models` at the top of your `__init__.py`
# so all models are registered when `db` is initialized.
# For simplicity and directness, I'll explicitly import.
from app.models import * # Import all models defined in app.models

def reset_database():
    """
    Drops all existing database tables and recreates them based on SQLAlchemy models.
    WARNING: This will permanently delete all data in the database.
    """
    app = create_app() # Assuming you have a create_app() function
    with app.app_context():
        print("--- Starting Database Reset ---")

        # 1. Drop all tables
        print("Dropping all existing database tables...")
        db.drop_all()
        print("All tables dropped.")

        # 2. Create all tables
        print("Creating new database tables...")
        db.create_all()
        print("All tables created successfully.")

        print("--- Database Reset Complete ---")

if __name__ == "__main__":
    # Ensure this script is run with proper environment setup
    # For Flask, this usually means having FLASK_APP and FLASK_ENV set
    # e.g., in your shell:
    # export FLASK_APP=run.py
    # export FLASK_ENV=development
    # python db_reset.py

    # Or if you have a .env file loaded by python-dotenv or similar
    
    reset_database()
