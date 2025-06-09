# run_arp_scan.py

from app import create_app, db
from app.models import Asset, NetworkSegment, AssetTier, BusinessUnit, DataClassification, Team # Import necessary models
from datetime import datetime
import subprocess
import re
import netifaces # For getting local network interface info
import ipaddress
import socket

def get_local_active_interface():
    """
    Attempts to determine the active network interface and its IP address.
    Prioritizes non-loopback, non-docker, and 'up' interfaces.
    Returns (interface_name, ip_address) or (None, None).
    """
    interfaces = netifaces.interfaces()
    for iface in interfaces:
        addrs = netifaces.ifaddresses(iface)
        if netifaces.AF_INET in addrs:
            for link in addrs[netifaces.AF_INET]:
                ip_address = link.get('addr')
                if ip_address and not ipaddress.ip_address(ip_address).is_loopback:
                    # Check if interface is up (basic check, more robust methods exist)
                    try:
                        # Attempt to get interface flags (requires specific OS knowledge or libraries)
                        # For simplicity, we'll assume if it has an IP and is not loopback/docker, it's active.
                        # You might need to check if 'UP' flag is set if more strictness is required.
                        if 'docker' in iface or 'veth' in iface: # Skip common virtual interfaces
                            continue
                        
                        # A simple check for a default route might be more reliable
                        gws = netifaces.gateways()
                        if gws.get('default') and gws['default'].get(netifaces.AF_INET):
                            default_iface = gws['default'][netifaces.AF_INET][1]
                            if iface == default_iface:
                                print(f"Detected active interface: {iface} with IP: {ip_address}")
                                return iface, ip_address
                    except Exception as e:
                        print(f"Warning: Could not check interface flags for {iface}: {e}")
                        pass
    print("Could not reliably determine an active non-loopback network interface.")
    return None, None

def run_arp_scan_and_save_to_db(interface=None, subnet_target=None):
    """
    Runs an arp-scan on the local subnet via the specified interface
    and saves the discovered assets to the database.
    """
    app = create_app()
    with app.app_context():
        print("--- Starting ARP Scan ---")

        if not interface or not subnet_target:
            detected_iface, detected_ip = get_local_active_interface()
            if not detected_iface or not detected_ip:
                print("Error: Could not determine active interface or IP. Please provide 'interface' and 'subnet_target' manually.")
                return

            if not interface: interface = detected_iface
            if not subnet_target:
                # Calculate subnet from detected IP and assumed /24 CIDR (common for LANs)
                # You might need to refine this to get actual netmask if you need more accuracy
                try:
                    network = ipaddress.ip_network(f"{detected_ip}/24", strict=False)
                    subnet_target = str(network)
                except ValueError:
                    print(f"Error: Could not determine subnet from IP {detected_ip}. Please provide 'subnet_target' manually.")
                    return

        print(f"Scanning on interface: {interface}, target: {subnet_target}")

        try:
            # -l: local host test (if on different subnet, remove)
            # -t: target hosts/network
            # -I: interface to use
            # --retry=3: Number of retries
            # -q: Quiet mode
            # -r 5: Retries each host 5 times
            # --plain: Plain output (no header/footer)
            # -g: Show arp-scan internal debugging messages (optional, remove for production)
            # Command to run arp-scan
            command = [
                'arp-scan',
                '-I', interface,
                '--localnet', # Scan local network (uses interface's IP and netmask)
                '--retry=3',
                '--quiet', # Suppress verbose output
                '--plain', # No header/footer
                # You can specify a target like this instead of --localnet:
                # subnet_target
            ]
            
            print(f"Executing command: {' '.join(command)}")
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            output = result.stdout

        except subprocess.CalledProcessError as e:
            print(f"ARP scan failed: {e}. Output:\n{e.stderr}")
            print("Please ensure arp-scan is installed and accessible in your PATH.")
            print("Also, arp-scan typically requires root privileges. Try running this script with 'sudo'.")
            return
        except FileNotFoundError:
            print("Error: 'arp-scan' command not found. Please install arp-scan.")
            return

        print("\n--- ARP Scan Results ---")
        # Regex to parse arp-scan plain output: IP_ADDRESS\tMAC_ADDRESS\tHOSTNAME
        # We are only interested in IP and MAC as hostname from arp-scan is often unreliable
        # or not configured for all devices.
        # Regex explanation:
        # ^                 - start of line
        # (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - capture group for IP address
        # \s+               - one or more whitespace characters
        # ([0-9a-fA-F]{2}(:[0-9a-fA-F]{2}){5}) - capture group for MAC address
        # (?:(\s+.*))?      - optional non-capturing group for hostname and rest (we ignore it)
        # $                 - end of line
        arp_entry_pattern = re.compile(r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+([0-9a-fA-F]{2}(:[0-9a-fA-F]{2}){5})(?:(\s+.*))?$')

        discovered_count = 0
        for line in output.splitlines():
            match = arp_entry_pattern.match(line.strip())
            if match:
                ip_address = match.group(1)
                mac_address = match.group(2).lower() # Store MAC as lowercase consistently
                
                print(f"  Found: IP={ip_address}, MAC={mac_address}")

                # Check if asset already exists
                asset = db.session.query(Asset).filter_by(ip_address=ip_address).first()

                if not asset:
                    # Lookup default values for FKs. Ensure these exist in your DB or handle gracefully.
                    # This assumes you have default entries in your lookup tables, e.g., an 'Unknown' entry with id=1
                    default_network_segment = db.session.query(NetworkSegment).filter_by(name='Unknown').first()
                    default_asset_tier = db.session.query(AssetTier).filter_by(name='Unknown').first()
                    default_business_unit = db.session.query(BusinessUnit).filter_by(name='Unknown').first()
                    default_data_classification = db.session.query(DataClassification).filter_by(name='Public').first()
                    default_owner_team = db.session.query(Team).filter_by(name='Unknown').first()

                    # Create new Asset
                    asset = Asset(
                        ip_address=ip_address,
                        mac_address=mac_address,
                        name=f"Host-{ip_address}", # Default hostname
                        os_type='Unknown', # ARP scan doesn't provide OS
                        os_version='Unknown', # ARP scan doesn't provide OS
                        last_scanned_date=datetime.utcnow(),
                        # Assign default FKs
                        network_segment_id=default_network_segment.id if default_network_segment else None,
                        asset_tier_id=default_asset_tier.id if default_asset_tier else None,
                        business_unit_id=default_business_unit.id if default_business_unit else None,
                        data_classification_id=default_data_classification.id if default_data_classification else None,
                        owner_team_id=default_owner_team.id if default_owner_team else None
                    )
                    db.session.add(asset)
                    print(f"    -> Added new Asset: {ip_address}")
                else:
                    # Update existing Asset's MAC address if different and last_scanned_date
                    if asset.mac_address != mac_address:
                        asset.mac_address = mac_address
                        print(f"    -> Updated MAC for existing Asset: {ip_address}")
                    asset.last_scanned_date = datetime.utcnow()
                    print(f"    -> Updated last_scanned_date for Asset: {ip_address}")
                
                discovered_count += 1
                db.session.commit() # Commit each asset to ensure it's available for subsequent lookups if needed

        print(f"\n--- ARP Scan Complete. Discovered {discovered_count} active hosts. ---")

if __name__ == '__main__':
    # Ensure FLASK_APP and FLASK_ENV are set in your environment
    # e.g., export FLASK_APP=run.py; export FLASK_ENV=development

    # --- IMPORTANT: Populate Lookup Tables if they are empty ---
    # This block ensures your FKs have valid values to reference.
    # You should adapt this to your actual default/initialization strategy.
    with create_app().app_context():
        try:
            if not db.session.query(NetworkSegment).filter_by(name='Unknown').first():
                db.session.add(NetworkSegment(name='Unknown', description='Default segment for unknown hosts'))
            if not db.session.query(AssetTier).filter_by(name='Unknown').first():
                db.session.add(AssetTier(name='Unknown', description='Default tier for unknown assets'))
            if not db.session.query(BusinessUnit).filter_by(name='Unknown').first():
                db.session.add(BusinessUnit(name='Unknown'))
            if not db.session.query(DataClassification).filter_by(name='Public').first(): # Or 'Unknown'
                db.session.add(DataClassification(name='Public', description='Default classification'))
            if not db.session.query(Team).filter_by(name='Unknown').first():
                db.session.add(Team(name='Unknown'))
            db.session.commit()
            print("Default lookup table entries ensured.")
        except Exception as e:
            db.session.rollback()
            print(f"Error ensuring default lookup entries: {e}")

    # You will likely need to run this script with sudo:
    # sudo python run_arp_scan.py

    # Or specify interface and subnet manually if auto-detection fails or you need specific targets:
    # run_arp_scan_and_save_to_db(interface='eth0', subnet_target='192.168.1.0/24')
    
    run_arp_scan_and_save_to_db()
