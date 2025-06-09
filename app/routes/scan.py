from datetime import datetime
from flask import Blueprint, request, jsonify
from app import db
from app.models import Scan, ScanResult, Asset, Port
import subprocess
import xml.etree.ElementTree as ET

scan_bp = Blueprint('scan', __name__, url_prefix='/scan')

@scan_bp.route('/')
def scan():
    return "Scan page - use POST /scan/run to start a scan"

@scan_bp.route('/run', methods=['POST'])
def run_scan():
    data = request.get_json()
    tool_name = data.get('tool_name')
    target = data.get('target')

    if not tool_name or not target:
        return jsonify({'error': 'tool_name and target are required'}), 400

    # Create scan record
    scan = Scan(tool_name=tool_name, target=target, started_at=datetime.utcnow())
    db.session.add(scan)
    db.session.commit()  # To get scan.id

    output = None

    try:
        if tool_name.lower() == "nmap":
            # Run nmap and capture XML output
            cmd = ["nmap", "-oX", "-", target]
            proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
            output = proc.stdout
            # Parse output and save Assets/ports
            parse_nmap_xml(output, scan)
        else:
            # Placeholder for other tools or simulate
            output = f"Simulated output for {tool_name} on {target}"

        # Save scan result
        scan_result = ScanResult(
            scan_id=scan.id,
            output=output,
            created_at=datetime.utcnow()
        )
        db.session.add(scan_result)
        
        scan.finished_at = datetime.utcnow()
        db.session.commit()

    except subprocess.CalledProcessError as e:
        db.session.rollback()
        return jsonify({'error': f'Scan command failed: {e}'}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Unexpected error: {e}'}), 500

    return jsonify({'scan_id': scan.id, 'message': 'Scan completed successfully'})

def parse_nmap_xml(xml_output, scan):
    """Parse Nmap XML output and save Assets and ports linked to the scan."""
    try:
        root = ET.fromstring(xml_output)

        for host in root.findall('host'):
            ip = None
            mac = None
            hostname = None

            # Extract IP
            addr_elem = host.find('address[@addrtype="ipv4"]')
            if addr_elem is not None:
                ip = addr_elem.attrib.get('addr')

            # Extract MAC
            mac_elem = host.find('address[@addrtype="mac"]')
            if mac_elem is not None:
                mac = mac_elem.attrib.get('addr')

            # Extract hostname
            hostnames = host.find('hostnames')
            if hostnames is not None and hostnames.find('hostname') is not None:
                hostname = hostnames.find('hostname').attrib.get('name')

            if ip:
                Asset = Asset.query.filter_by(ip_address=ip).first()
                if not Asset:
                    Asset = Asset(
                        ip_address=ip,
                        mac_address=mac,
                        hostname=hostname,
                        last_seen=datetime.utcnow()
                    )
                    db.session.add(Asset)
                else:
                    Asset.last_seen = datetime.utcnow()
                    if mac:
                        Asset.mac_address = mac
                    if hostname:
                        Asset.hostname = hostname
                db.session.flush()  # Ensure Asset.id is available

                # Link scan result to Asset
                # Assuming scan_result has Asset_id; if not, adjust accordingly
                # We'll assign this in the calling function or adapt model

                # Parse ports
                ports_elem = host.find('ports')
                if ports_elem is not None:
                    for port in ports_elem.findall('port'):
                        port_num = int(port.attrib.get('portid'))
                        protocol = port.attrib.get('protocol')
                        state_elem = port.find('state')
                        state = state_elem.attrib.get('state') if state_elem is not None else None
                        service_elem = port.find('service')
                        service_name = service_elem.attrib.get('name') if service_elem is not None else None

                        existing_port = Port.query.filter_by(
                            Asset_id=Asset.id,
                            port_number=port_num,
                            protocol=protocol
                        ).first()

                        if not existing_port:
                            new_port = Port(
                                Asset_id=Asset.id,
                                port_number=port_num,
                                protocol=protocol,
                                state=state,
                                service_name=service_name
                            )
                            db.session.add(new_port)
                        else:
                            existing_port.state = state
                            existing_port.service_name = service_name

        db.session.flush()
    except ET.ParseError:
        # Just skip parsing if invalid XML, but scan result still saved
        pass
