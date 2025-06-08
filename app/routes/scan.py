#lantern/app/routes/scan.py
from datetime import datetime
from flask import Blueprint
from app import db
from app.models import Scan, ScanResult, Device, Port, Vulnerability, Credential
import subprocess
import xml.etree.ElementTree as ET

scan_bp = Blueprint('scan', __name__, url_prefix='/scan')

@scan_bp.route('/')
def scan_home():
    return "Scan page"


def run_scan(tool_name, target):
    # 1. Record scan metadata
    scan = Scan(tool_name=tool_name, target=target, started_at=datetime.utcnow())
    db.session.add(scan)
    db.session.commit()

    # 2. Execute scan
    if tool_name.lower() == "nmap":
        cmd = ["nmap", "-oX", "-", target]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        output = proc.stdout
    else:
        output = f"Simulated output for {tool_name} on {target}"

    # 3. Save raw result
    scan_result = ScanResult(
        scan_id=scan.id,
        output=output,
        created_at=datetime.utcnow()
    )
    db.session.add(scan_result)

    # 4. Parse results if Nmap
    if tool_name.lower() == "nmap":
        try:
            root = ET.fromstring(output)
            for host in root.findall("host"):
                ip = None
                mac = None
                hostname = None

                addr_elem = host.find('address[@addrtype="ipv4"]')
                if addr_elem is not None:
                    ip = addr_elem.attrib.get("addr")

                mac_elem = host.find('address[@addrtype="mac"]')
                if mac_elem is not None:
                    mac = mac_elem.attrib.get("addr")

                hostnames = host.find("hostnames")
                if hostnames is not None and hostnames.find("hostname") is not None:
                    hostname = hostnames.find("hostname").attrib.get("name")

                # 5. Create or update Device
                if ip:
                    device = Device.query.filter_by(ip_address=ip).first()
                    if not device:
                        device = Device(ip_address=ip, mac_address=mac, hostname=hostname, last_seen=datetime.utcnow())
                        db.session.add(device)
                        db.session.flush()  # Ensure device.id is available
                    else:
                        device.last_seen = datetime.utcnow()
                        if mac:
                            device.mac_address = mac
                        if hostname:
                            device.hostname = hostname

                    # 6. Pull credentials (if they exist)
                    creds = Credential.query.filter_by(device_id=device.id).first()
                    if creds:
                        print(f"🔐 Found credentials for {ip} — {creds.username}:{creds.password}")
                        # Place your tool-specific logic here to use these creds

                    # 7. Parse and save open ports
                    ports_elem = host.find("ports")
                    if ports_elem is not None:
                        for port in ports_elem.findall("port"):
                            port_id = int(port.attrib.get("portid"))
                            protocol = port.attrib.get("protocol")
                            state = port.find("state").attrib.get("state")
                            service_elem = port.find("service")
                            service_name = service_elem.attrib.get("name") if service_elem is not None else None

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

                    # 8. Link scan result to device
                    scan_result.device_id = device.id

        except ET.ParseError:
            print("❌ Failed to parse Nmap output as XML")

    # 9. Finalize
    scan.finished_at = datetime.utcnow()
    db.session.commit()
    return scan.id
