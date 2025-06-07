#!/bin/bash

set -e

echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

echo "Installing Python3, pip, and virtualenv..."
sudo apt install -y python3 python3-pip python3-venv

echo "Installing PostgreSQL server and contrib..."
sudo apt install -y postgresql postgresql-contrib

echo "Starting and enabling PostgreSQL service..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

echo "Creating PostgreSQL database and user..."

sudo -u postgres psql <<EOF
CREATE DATABASE lanterndb;
CREATE USER lanternuser WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE lanterndb TO lanternuser;
EOF

echo "Setting up Python virtual environment..."
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

