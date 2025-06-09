# run_nmap_scan.py

from app import create_app, db
from app.models import Scan, Asset, Port, InstalledApplication # Import necessary models
from datetime import datetime
import nmap
import ipaddress
import socket
import netifaces # For getting local network interface info

def get_local_subnet():
    """
    Attempts to determine the local host's IP address and subnet.
    Prioritizes non-loopback, non-docker interfaces.
    """
    interfaces = netifaces.interfaces()
    for iface in interfaces:
        addresses = netifaces.ifaddresses(iface)
        if netifaces.AF_INET in addresses:
            for link in addresses[netifaces.AF_INET]:
                ip_address = link['addr']
                netmask = link['netmask']

                # Skip loopback and common Docker interfaces
                if ipaddress.ip_address(ip_address).is_loopback or 'docker' in iface or 'veth' in iface:
                    continue

                try:
                    # Construct subnet in CIDR notation
                    network = ipaddress.ip_network(f"{ip_address}/{netmask}", strict=False)
                    print(f"Detected local IP: {ip_address}, Netmask: {netmask}, Subnet: {network}")
                    return str(network)
                except ValueError:
                    continue # Not a valid IP/netmask combo for ipaddress

    print("Could not reliably determine local subnet. Defaulting to a common /24 (192.168.1.0/24).")
    return "192.168.1.0/24" # Fallback, adjust as necessary for your environment


def run_nmap_scan_and_save_to_db(subnet_target=None):
    """
    Runs an Nmap scan on the specified subnet and saves the results to the database.
    """
    app = create_app()
    with app.app_context():
        print("--- Starting Nmap Scan ---")

        if not subnet_target:
            subnet_target = get_local_subnet()
            if not subnet_target:
                print("Error: Could not determine subnet and no target was provided.")
                return

        print(f"Scanning subnet: {subnet_target}")

        nm = nmap.PortScanner()
        
        # Nmap scan arguments:
        # -sS: SYN scan (stealthy)
        # -sV: Version detection (for service names and versions)
        # -O: OS detection
        # -T4: Aggressive timing
        # -oX -: Output XML to stdout (python-nmap parses this)
        # --min-rate 1000: Minimum packet rate to speed up, be cautious on small networks
        # -p 1-1024,8080,8443: Scan common ports and some web app ports. Customize as needed.
        nmap_args = "-sS -sV -O -T4 -oX - --min-rate 1000 -p 1-1024,8080,8443"
        
        print(f"Running Nmap with arguments: {nmap_args}")
        
        scan_start_time = datetime.utcnow()
        try:
            nm.scan(hosts=subnet_target, arguments=nmap_args)
            scan_end_time = datetime.utcnow()
        except nmap.PortScannerError as e:
            print(f"Nmap scan failed: {e}. Please ensure Nmap is installed and accessible in your PATH, and you have necessary permissions (e.g., run with sudo).")
            return

        # Create a new Scan entry in the database
        new_scan = Scan(
            tool_name='Nmap',
            target=subnet_target,
            started_at=scan_start_time,
            finished_at=scan_end_time
        )
        db.session.add(new_scan)
        db.session.commit()
        print(f"Scan entry created in DB (ID: {new_scan.id}).")

        # Process Nmap scan results
        for host in nm.all_hosts():
            print(f"\nProcessing host: {host} ({nm[host].hostname()})")

            # Check if host is up
            if nm[host].state() != 'up':
                print(f"Host {host} is {nm[host].state()}, skipping detailed processing.")
                continue

            ip_address = host
            hostname = nm[host].hostname() if nm[host].hostname() else None # Use hostname if available

            # Try to get MAC address
            mac_address = None
            if 'addresses' in nm[host] and 'mac' in nm[host]['addresses']:
                mac_address = nm[host]['addresses']['mac']

            # Retrieve or create Asset
            asset = db.session.query(Asset).filter_by(ip_address=ip_address).first()
            if not asset:
                # Basic OS info from Nmap. Nmap's OS detection is best effort.
                os_type = 'Unknown'
                os_version = 'Unknown'
                if 'osmatch' in nm[host]:
                    for osmatch in nm[host]['osmatch']:
                        if osmatch['accuracy'] > 80: # Consider a high confidence match
                            os_type = osmatch['name'].split(' ')[0] # Take first word as OS type
                            os_version = osmatch['name'] # Full OS description
                            break
                
                print(f"Creating new Asset: {ip_address}")
                asset = Asset(
                    ip_address=ip_address,
                    name=hostname,
                    mac_address=mac_address,
                    os_type=os_type,
                    os_version=os_version,
                    last_scanned_date=datetime.utcnow(),
                    # Default values for required FKs - you'll want to populate these
                    # with proper lookup values based on your environment
                    asset_tier_id=1, # Default to a generic tier, e.g., 'Unknown' or 'Low'
                    business_unit_id=1, # Default to 'Unknown'
                    data_classification_id=1, # Default to 'Public'
                    network_segment_id=1, # Default to 'Unknown'
                    owner_team_id=1 # Default to 'Unknown'
                )
                db.session.add(asset)
                db.session.commit() # Commit to get asset.id for relationships
            else:
                # Update existing asset's last seen/scanned date
                asset.last_scanned_date = datetime.utcnow()
                asset.name = hostname if hostname else asset.name # Update hostname if found
                asset.mac_address = mac_address if mac_address else asset.mac_address
                db.session.commit()
                print(f"Updated existing Asset: {ip_address}")

            # Create a ScanResult entry for this asset within the scan
            # Note: The 'output' field from original ScanResult is no longer relevant for misconfigs.
            # We'll link AssetMisconfigurations to this ScanResult.
            scan_result_entry = db.session.query(ScanResult).filter_by(
                scan_id=new_scan.id, asset_id=asset.id
            ).first()
            if not scan_result_entry:
                scan_result_entry = ScanResult(
                    scan_id=new_scan.id,
                    asset_id=asset.id,
                    raw_scan_output_summary=nm[host].state() # Simple state as summary
                )
                db.session.add(scan_result_entry)
                db.session.commit()
            
            # Add Port information
            for proto in nm[host].all_protocols():
                lport = nm[host][proto].keys()
                for port in lport:
                    port_info = nm[host][proto][port]
                    print(f"  Port: {port}/{proto} State: {port_info['state']}")
                    
                    # Check if port already exists for this asset
                    existing_port = db.session.query(Port).filter_by(
                        asset_id=asset.id, port_number=port, protocol=proto
                    ).first()

                    if not existing_port:
                        new_port = Port(
                            asset_id=asset.id,
                            port_number=port,
                            protocol=proto,
                            service_name=port_info.get('name'),
                            state=port_info.get('state')
                        )
                        db.session.add(new_port)
                    else:
                        # Update existing port state/service info
                        existing_port.state = port_info.get('state')
                        existing_port.service_name = port_info.get('name')

                    # Add InstalledApplication based on service
                    if port_info.get('product'):
                        app_name = port_info['product']
                        app_version = port_info.get('version', 'Unknown')
                        
                        existing_app = db.session.query(InstalledApplication).filter_by(
                            asset_id=asset.id,
                            application_name=app_name,
                            version=app_version
                        ).first()

                        if not existing_app:
                            new_app = InstalledApplication(
                                asset_id=asset.id,
                                application_name=app_name,
                                version=app_version
                            )
                            db.session.add(new_app)
            db.session.commit() # Commit all changes for the current host

        print("\n--- Nmap Scan and Database Save Complete ---")

if __name__ == '__main__':
    # Ensure FLASK_APP and FLASK_ENV are set in your environment
    # e.g., export FLASK_APP=run.py; export FLASK_ENV=development
    
    # You might need to populate your lookup tables first if they are empty
    # For a quick start, ensure you have default entries in:
    # AssetTier, BusinessUnit, DataClassification, NetworkSegment, Team
    # Example (add this logic if needed for initial setup):
    # with create_app().app_context():
    #     if not db.session.query(AssetTier).first():
    #         db.session.add(AssetTier(id=1, name='Unknown', description='Default unknown tier'))
    #         db.session.add(BusinessUnit(id=1, name='Unknown'))
    #         db.session.add(DataClassification(id=1, name='Public'))
    #         db.session.add(NetworkSegment(id=1, name='Unknown'))
    #         db.session.add(Team(id=1, name='Unknown'))
    #         db.session.commit()

    run_nmap_scan_and_save_to_db()
    # Or, to scan a specific subnet:
    # run_nmap_scan_and_save_to_db("192.168.1.0/24")
