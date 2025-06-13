#!/bin/bash
set -e

REPO_URL="https://github.com/bailey189/lantern.git"
PROJECT_DIR="lantern"
DB_NAME="lanterndb"
DB_USER="lanternuser"
DB_PASS="yourpassword"

echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

echo "Installing required packages..."
sudo apt install -y python3 python3-pip python3-venv git postgresql postgresql-contrib net-tools nmap

echo "Cloning or updating the Lantern repository..."
if [ -d "$PROJECT_DIR/.git" ]; then
    echo "Git repository found. Pulling latest changes..."
    cd "$PROJECT_DIR"
    git pull origin main
    cd ..
else
    echo "Cloning repository from $REPO_URL ..."
    git clone "$REPO_URL" "$PROJECT_DIR"
fi

echo "Starting and enabling PostgreSQL service..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

echo "Creating PostgreSQL database and user (if not exists)..."
sudo -u postgres psql <<EOF
DO
\$do\$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_database WHERE datname = '${DB_NAME}'
   ) THEN
      CREATE DATABASE ${DB_NAME};
   END IF;
END
\$do\$;

DO
\$do\$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles WHERE rolname = '${DB_USER}'
   ) THEN
      CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASS}';
      GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};
   END IF;
END
\$do\$;
EOF

echo "Setting up Python virtual environment..."
cd "$PROJECT_DIR"
python3 -m venv venv
source venv/bin/activate

echo "Upgrading pip and installing dependencies..."
pip install --upgrade pip

if [ -f requirements.txt ]; then
    pip install -r requirements.txt
fi

echo "Installing PostgreSQL Python driver and netifaces..."
pip install psycopg2-binary netifaces

echo "Running database migrations..."
flask db upgrade

echo "Populating AssetTier table..."
flask populate-assettier

echo "Setup complete."
echo "Remember to update your config.py with:"
echo "SQLALCHEMY_DATABASE_URI = 'postgresql://${DB_USER}:${DB_PASS}@localhost:5432/${DB_NAME}'"
echo "To activate your environment: source venv/bin/activate"
echo "To run the app: flask run"