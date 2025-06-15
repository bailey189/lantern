import hashlib
import os
from getpass import getpass
from flask import Flask
from dotenv import load_dotenv
from cryptography.fernet import Fernet

# Load environment variables from .env file
load_dotenv()

# Check if FERNET_KEY is set, if not, create and save it
if not os.environ.get("FERNET_KEY"):
    print("❌ FERNET_KEY not found in environment variables.")
    key = Fernet.generate_key().decode()
    with open(".env", "a") as f:
        f.write(f"\nFERNET_KEY={key}\n")
    print("✅ FERNET_KEY generated and added to .env. Please restart the application.")
    exit(1)

from app import create_app

# Ensure the config object is passed to create_app
app = create_app('config.Config')

def validate_license():
    print("🔐 Lantern License Verification")
    license_key = getpass("Enter your license key: ")
    hashed_input = hashlib.md5(license_key.encode()).hexdigest()

    if hashed_input == VALID_LICENSE_HASH:
        print("✅ License verified. Starting application...")
        return True
    else:
        print("❌ Invalid license key. Access denied.")
        return False


if __name__ == "__main__":
    if validate_license():
        app = create_app()
        app.run(host='0.0.0.0', port=5000)