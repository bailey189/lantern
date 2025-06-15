import hashlib
import os
from getpass import getpass
from flask import Flask
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

if not os.environ.get("FERNET_KEY"):
    print("❌ FERNET_KEY not found in environment variables.")
    key = Fernet.generate_key().decode()
    with open('.env', 'a') as f:
        f.write(f'\nFERNET_KEY={key}\n')
    from cryptography.fernet import Fernet
    fernet = Fernet(key)
    print("🔑 FERNET_KEY generated and saved to .env file.")
    with open("license.txt", "a") as file:
        file.write("This is your FERNET_KEY={key}.\n")

# Expected MD5 hash of the correct license key
VALID_LICENSE_HASH = "54fa7e778bd1c624aa2ac67785f6c798"
from app import create_app

app = create_app()

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


if __name__ == '__main__':
    if validate_license():
        app.run(host='0.0.0.0', port=5000)

