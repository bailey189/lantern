import hashlib
from getpass import getpass
from app import create_app
from flask import Flask

# Expected MD5 hash of the correct license key
VALID_LICENSE_HASH = "54fa7e778bd1c624aa2ac67785f6c798"

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
        app = create_app()
        app.run(host='0.0.0.0', port=5000)
