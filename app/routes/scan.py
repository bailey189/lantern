from datetime import datetime
from flask import Blueprint, request, jsonify, render_template
from app import db
from app.models import Scan, ScanResult, Asset, Port
import subprocess
import xml.etree.ElementTree as ET
import netifaces

scan_bp = Blueprint('scan', url_prefix='/scan')

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
            cmd = ["nmap", "-sn", subnet]
            proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
            discovery_result = proc.stdout
            # Optionally parse and save assets here if needed
            scan_result = ScanResult(
                scan_id=scan.id,
                output=discovery_result,
                created_at=datetime.utcnow()
            )
            db.session.add(scan_result)
            scan.finished_at = datetime.utcnow()
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            error = f"Error running nmap: {e}"

    return render_template('scan.html', title="Lantern - Scan", discovery_result=discovery_result, error=error)

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
