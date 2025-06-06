# update_lantern.sh
# Bash script to sync Lantern project on Raspberry Pi and install dependencies

#!/bin/bash

# CONFIGURATION
REPO_URL="https://github.com/bailey189/lantern.git"
PROJECT_DIR="/home/pi/lantern"
VENV_DIR="$PROJECT_DIR/venv"

# Ensure script is run as pi
if [ "$EUID" -ne 1000 ]; then
  echo "Please run this script as the 'pi' user (UID 1000)."
  exit 1
fi

# Clone or update the repo
if [ ! -d "$PROJECT_DIR/.git" ]; then
  echo "Cloning Lantern project..."
  git clone "$REPO_URL" "$PROJECT_DIR"
else
  echo "Updating existing Lantern project..."
  cd "$PROJECT_DIR" || exit
  git pull origin main
fi

# Set up virtual environment if not already created
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment..."
  python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Install/update Python dependencies
if [ -f "$PROJECT_DIR/requirements.txt" ]; then
  echo "Installing Python dependencies..."
  pip install --upgrade pip
  pip install -r "$PROJECT_DIR/requirements.txt"
else
  echo "No requirements.txt found. Skipping pip install."
fi

# Deactivate venv
deactivate

echo "Lantern project is up to date."
