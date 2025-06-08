#!/bin/bash
mkdir lantern
cd /lantern
apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib
apt install -y git

set -e

REPO_URL="https://github.com/bailey189/lantern.git"
PROJECT_DIR="lantern"

if [ -d "$PROJECT_DIR/.git" ]; then
    echo "Git repository found. Pulling latest changes..."
    cd "$PROJECT_DIR"
    git pull origin main
    cd ..
else
    echo "Cloning repository from $REPO_URL ..."
    git clone "$REPO_URL" "$PROJECT_DIR"
fi

echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

echo "Installing Python3, pip, and virtualenv..."
sudo apt install -y python3 python3-pip python3-venv git postgresql postgresql-contrib

echo "Starting and enabling PostgreSQL service..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

echo "Creating PostgreSQL database and user (if not exists)..."
sudo -u postgres psql <<EOF
DO
\$do\$
BEGIN
   IF NOT EXISTS (
      SELECT
      FROM   pg_catalog.pg_database
      WHERE  datname = 'lanterndb'
   ) THEN
      CREATE DATABASE lanterndb;
   END IF;
END
\$do\$;

DO
\$do\$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles WHERE rolname = 'lanternuser'
   ) THEN
      CREATE USER lanternuser WITH PASSWORD 'yourpassword';
      GRANT ALL PRIVILEGES ON DATABASE lanterndb TO lanternuser;
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

echo "Installing PostgreSQL Python driver..."
pip install psycopg2-binary

echo "Setup complete. Remember to update your config.py with PostgreSQL URI:"
echo "postgresql://lanternuser:yourpassword@localhost:5432/lanterndb"
