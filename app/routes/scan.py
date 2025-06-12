from datetime import datetime
from flask import Blueprint, request, jsonify, render_template
from app import db
from app.models import Scan, ScanResult, Asset, Port
import subprocess
import xml.etree.ElementTree as ET
import netifaces

scan_bp = Blueprint('scan', __name__, url_prefix='/scan')

def get_default_subnet():
    # This will get the first non-loopback IPv4 address and its subnet
    for iface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(iface)
        if netifaces.AF_INET in addrs:
            for addr in addrs[netifaces.AF_INET]:
                ip = addr.get('addr')
                netmask = addr.get('netmask')
                if ip and netmask and not ip.startswith('127.'):
                    # Calculate CIDR
                    bits = sum([bin(int(x)).count('1') for x in netmask.split('.')])
                    subnet = f"{ip.rsplit('.',1)[0]}.0/{bits}"
                    return subnet
    return "192.168.1.0/24"

@scan_bp.route('/', methods=['GET'])
def scan():
    subnet = get_default_subnet()
    return render_template('scan.html', title="Lantern - Scan", subnet=subnet)

@scan_bp.route('/discovery', methods=['POST'])
def discovery_scan():
    subnet = request.form.get('subnet')
    discovery_result = None
    error = None

    if not subnet:
        error = "Subnet is required for discovery scan."
    else:
        scan = Scan(tool_name="nmap", target=subnet, started_at=datetime.utcnow())
        db.session.add(scan)
        db.session.commit()
        try:
            # Use grepable output for easier parsing
            started_at=datetime.utcnow()
            cmd = ["nmap", "-sn", "-oG", "-", subnet]
            proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
            discovery_result = proc.stdout
            finished_at=datetime.utcnow()
            # Parse nmap output and update Asset table
            for line in discovery_result.splitlines():
                if line.startswith("Host:") or "Status: Up" in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        ip = parts[1]
                        # Try to get hostname if present
                        hostname = None
                        if "(" in line and ")" in line:
                            hostname = line.split("(")[1].split(")")[0].strip()
                        # Check if asset exists
                        asset = Asset.query.filter_by(ip_address=ip).first()
                        if asset:
                            asset.last_scanned_date = datetime.utcnow()
                            if hostname:
                                asset.name = hostname
                        else:
                            asset = Asset(
                                ip_address=ip,
                                name=hostname or ip,
                                os_type="Unknown",        # Placeholder, update if you can detect
                                os_version="Unknown",     # Placeholder, update if you can detect
                                last_scanned_date=datetime.utcnow(),
                                is_active=True
                            )
                            db.session.add(asset)
            db.session.commit()

            # After discovery, run OS/service scan for assets with unknown OS
            unknown_assets = Asset.query.filter_by(os_type="Unknown").all()
            for asset in unknown_assets:
                try:
                    os_scan_cmd = [
                       "sudo", "nmap", "-O", "-sV", "--script=afp-serverinfo", asset.ip_address
                    ]
                    os_proc = subprocess.run(os_scan_cmd, capture_output=True, text=True, timeout=60)
                    os_output = os_proc.stdout

                    # Basic parsing for OS and service info
                    os_type = "Unknown"
                    os_version = "Unknown"
                    mac_address = None

                    for line in os_output.splitlines():
                        if line.strip().startswith("OS details:"):
                            os_type = line.split(":", 1)[1].strip()
                        elif line.strip().startswith("MAC Address:"):
                            mac_address = line.split(":", 1)[1].split()[0].strip()
                        elif "Running:" in line:
                            os_type = line.split(":", 1)[1].strip()
                        elif "Service Info:" in line:
                            os_version = line.split(":", 1)[1].strip()

                    asset.os_type = os_type
                    asset.os_version = os_version
                    if mac_address:
                        asset.mac_address = mac_address

                    db.session.commit()
                except Exception as e:
                    # Optionally log or handle errors for individual asset scans
                    continue

            scan_result = ScanResult(
                scan_id=scan.id,
                output=discovery_result,
                started_at=started_at,
                finished_at=finished_at
            )
            db.session.add(scan_result)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            error = f"Error running nmap: {e}"

    return render_template('scan.html', title="Lantern - Scan", discovery_result=discovery_result, error=error)

@scan_bp.route('/erase_all', methods=['POST'])
def erase_all():
    try:
        # Delete from child tables first due to FK constraints
        db.session.query(Port).delete()
        db.session.query(ScanResult).delete()
        db.session.query(Scan).delete()
        db.session.query(Asset).delete()
        db.session.commit()
        msg = "All scan, asset, and port records have been erased."
    except Exception as e:
        db.session.rollback()
        msg = f"Error erasing records: {e}"
    return render_template('scan.html', title="Lantern - Scan", error=None, discovery_result=None, portscan_result=None, arpscan_result=None, erase_msg=msg)

@scan_bp.route('/port', methods=['POST'])
def port_scan():
    subnet = request.form.get('subnet')
    ports = request.form.get('ports')
    portscan_result = None
    error = None

    if not subnet or not ports:
        error = "Subnet and ports are required for port scan."
    else:
        scan = Scan(tool_name="masscan", target=subnet, started_at=datetime.utcnow())
        db.session.add(scan)
        db.session.commit()
        try:
            cmd = ["masscan", subnet, "-p", ports, "--rate", "1000"]
            proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
            portscan_result = proc.stdout
            scan_result = ScanResult(
                scan_id=scan.id,
                output=portscan_result,
                created_at=datetime.utcnow()
            )
            db.session.add(scan_result)
            scan.finished_at = datetime.utcnow()
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            error = f"Error running masscan: {e}"

    return render_template('scan.html', title="Lantern - Scan", portscan_result=portscan_result, error=error)

@scan_bp.route('/arp', methods=['POST'])
def arp_scan():
    arpscan_result = None
    error = None

    scan = Scan(tool_name="arp-scan", target="local", started_at=datetime.utcnow())
    db.session.add(scan)
    db.session.commit()
    try:
        # Example command; adjust as needed for your environment
        cmd = ["arp", "-a"]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        arpscan_result = proc.stdout
        scan_result = ScanResult(
            scan_id=scan.id,
            output=arpscan_result,
            created_at=datetime.utcnow()
        )
        db.session.add(scan_result)
        scan.finished_at = datetime.utcnow()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        error = f"Error running ARP scan: {e}"

    return render_template('scan.html', title="Lantern - Scan", arpscan_result=arpscan_result, error=error)
