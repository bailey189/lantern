#lantern/app/routes/scan.py
from datetime import datetime
from app import db
from app.models import Scan, ScanResult, Device, Port, Vulnerability
from flask import Blueprint, request, render_template
import subprocess

scan_bp = Blueprint('scan', __name__, url_prefix='/scan')

@scan_bp.route('/')
@scan_bp.route('/run', methods=['GET', 'POST'])

def scan_home():
    return "Scan page"

def run():
    if request.method == 'POST':
        tool = request.form.get('tool')
        target = request.form.get('target')
        if not tool or not target:
            return "Tool and target are required", 400
        
        scan_id = run_scan(tool, target)
        return f"Scan started with ID: {scan_id}"
    
    # For GET, just show the form
    tools = [
        "Nmap",
        "Masscan",
        "AngryIPScanner",
        "Arp-scan",
        "Dhcpdump",
        "Kismet",
        "Aircrack-ng",
        "Hping3",
        "Nikto",
        "Wapiti",
        "Skipfish",
        "SQLmap",
        "Trivy",
        "Ansible"
    ]
    return render_template('scan_run.html', tools=tools)
    
def run_scan(tool_name, target):
    # Create a new Scan record
    scan = Scan(tool_name=tool_name, target=target, started_at=datetime.utcnow())
    db.session.add(scan)
    db.session.commit()  # Commit to generate scan.id

    # Example: run nmap scan, you should customize for other tools similarly
    if tool_name.lower() == "nmap":
        cmd = ["nmap", "-oX", "-", target]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        output = proc.stdout
    else:
        # placeholder for other tools
        output = f"Simulated output for {tool_name} on {target}"

    # Save scan result
    scan_result = ScanResult(
        scan_id=scan.id,
        output=output,
        created_at=datetime.utcnow()
    )
    db.session.add(scan_result)

    # Parse output to find devices and ports (simplified example for nmap XML)
    if tool_name.lower() == "nmap":
        import xml.etree.ElementTree as ET
        try:
            root = ET.fromstring(output)
            for host in root.findall("host"):
                ip = None
                mac = None
                hostname = None

                # IP
                addr_elem = host.find('address[@addrtype="ipv4"]')
                if addr_elem is not None:
                    ip = addr_elem.attrib.get("addr")

                # MAC
                mac_elem = host.find('address[@addrtype="mac"]')
                if mac_elem is not None:
                    mac = mac_elem.attrib.get("addr")

                # Hostname
                hostnames = host.find("hostnames")
                if hostnames is not None and hostnames.find("hostname") is not None:
                    hostname = hostnames.find("hostname").attrib.get("name")

                # Create or update Device
                if ip:
                    device = Device.query.filter_by(ip_address=ip).first()
                    if not device:
                        device = Device(ip_address=ip, mac_address=mac, hostname=hostname, last_seen=datetime.utcnow())
                        db.session.add(device)
                    else:
                        device.last_seen = datetime.utcnow()
                        if mac:
                            device.mac_address = mac
                        if hostname:
                            device.hostname = hostname

                    db.session.flush()  # Get device.id for ports

                    # Ports
                    ports_elem = host.find("ports")
                    if ports_elem is not None:
                        for port in ports_elem.findall("port"):
                            port_id = int(port.attrib.get("portid"))
                            protocol = port.attrib.get("protocol")
                            state = port.find("state").attrib.get("state")
                            service_elem = port.find("service")
                            service_name = service_elem.attrib.get("name") if service_elem is not None else None

                            # Check if port exists for device
                            existing_port = Port.query.filter_by(device_id=device.id, port_number=port_id, protocol=protocol).first()
                            if not existing_port:
                                new_port = Port(
                                    device_id=device.id,
                                    port_number=port_id,
                                    protocol=protocol,
                                    state=state,
                                    service_name=service_name,
                                )
                                db.session.add(new_port)
                            else:
                                existing_port.state = state
                                existing_port.service_name = service_name

                    # Link scan_result to device
                    scan_result.device_id = device.id

        except ET.ParseError:
            # If XML parsing fails, just keep the output in ScanResult
            pass

    scan.finished_at = datetime.utcnow()
    db.session.commit()
    return scan.id
