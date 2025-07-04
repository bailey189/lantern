#!/bin/bash

# update_lantern.sh - Syncs local Lantern project with the latest GitHub repository version

# Set variables
REPO_URL="https://github.com/bailey189/lantern.git"
PROJECT_DIR="$HOME/lantern"
BACKUP_DIR="$HOME/lantern_backup_$(date +%Y%m%d_%H%M%S)"

echo ">>> Updating Lantern Project"

# Ensure script is not run as root
if [[ $EUID -eq 0 ]]; then
  echo "Please do not run this script as root. Exiting."
  exit 1
fi

# Backup current project
if [ -d "$PROJECT_DIR" ]; then
  echo ">>> Backing up current project to $BACKUP_DIR"
  cp -r "$PROJECT_DIR" "$BACKUP_DIR"
else
  echo ">>> No existing Lantern project found at $PROJECT_DIR. Skipping backup."
fi

# Clone into a temporary directory
TMP_DIR=$(mktemp -d)
echo ">>> Cloning repository into temporary directory $TMP_DIR"
git clone "$REPO_URL" "$TMP_DIR"

if [ $? -ne 0 ]; then
  echo "!!! Git clone failed. Exiting."
  exit 1
fi

# Sync the files using rsync (preserves permissions, avoids deleting venv or local data folders)
echo ">>> Syncing files into $PROJECT_DIR"
rsync -av --exclude='venv' --exclude='data' --exclude='instance' --exclude='.git' "$TMP_DIR/" "$PROJECT_DIR/"

# Clean up
echo ">>> Cleaning up temporary directory"
rm -rf "$TMP_DIR"

# Optionally update Python dependencies
echo ">>> Updating Python dependencies"
source "$PROJECT_DIR/venv/bin/activate"
pip install -r "$PROJECT_DIR/requirements.txt"

chmod +x update_lantern.sh
chmod +x setup.sh

echo ">>> Update complete!"


# Kill any running run.py processes
echo "Stopping existing run.py processes..."
pkill -f "python.*run.py"

# Wait a moment to ensure processes are stopped
sleep 2

# Start run.py in the background using the same Python interpreter as the venv
echo "Starting run.py..."
cd /home/pi/lantern
source venv/bin/activate
nohup python run.py > lantern.log 2>&1 &

echo "run.py has been restarted."
