#!/bin/bash
set -e

echo "Updating package lists..."
sudo apt update

echo "Installing packages from apt..."
sudo apt install -y \
  nmap masscan arp-scan dhcpdump aircrack-ng hping3 nikto wapiti sqlmap ansible curl

echo "Installing Trivy..."
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sudo sh -s -- -b /usr/local/bin

echo "Installing Angry IP Scanner..."
# Download latest Angry IP Scanner deb package for Debian/Ubuntu (arm64 or amd64)
ARCH=$(dpkg --print-architecture)
if [[ "$ARCH" == "arm64" ]]; then
  # ARM64 version link (check official site for updates)
  AIPSCURRENT="3.8.6"
  AIPSURL="https://github.com/angryip/ipscan/releases/download/${AIPSCURRENT}/ipscan_${AIPSCURRENT}_arm64.deb"
elif [[ "$ARCH" == "amd64" ]]; then
  AIPSCURRENT="3.8.6"
  AIPSURL="https://github.com/angryip/ipscan/releases/download/${AIPSCURRENT}/ipscan_${AIPSCURRENT}_amd64.deb"
else
  echo "Unsupported architecture $ARCH for Angry IP Scanner. Please install manually."
  exit 1
fi

TMPDEB=$(mktemp --suffix=.deb)
curl -L "$AIPSURL" -o "$TMPDEB"
sudo dpkg -i "$TMPDEB" || sudo apt-get install -f -y
rm -f "$TMPDEB"

cd /usr/share/nmap/scripts
wget https://raw.githubusercontent.com/scipag/vulscan/master/vulscan.nse

echo "All tools installed successfully."
