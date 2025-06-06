import xml.etree.ElementTree as ET
from app.models import db, Device


def parse_nmap_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    hosts = []

    for host in root.findall('host'):
        ip_elem = host.find("address[@addrtype='ipv4']")
        ip = ip_elem.attrib['addr'] if ip_elem is not None else None

        mac_elem = host.find("address[@addrtype='mac']")
        mac = mac_elem.attrib['addr'] if mac_elem is not None else None

        name_elem = host.find('hostnames/hostname')
        hostname = name_elem.attrib['name'] if name_elem is not None else 'Unknown'

        os = 'Unknown'
        os_elem = host.find('os')
        if os_elem is not None:
            os_match = os_elem.find('osmatch')
            if os_match is not None:
                os = os_match.attrib.get('name', 'Unknown')

        if ip:
            device = Device.query.filter_by(ip_address=ip).first()
            if not device:
                device = Device(ip_address=ip)
            device.hostname = hostname
            device.mac_address = mac
            device.operating_system = os
            db.session.add(device)
            hosts.append(device)

    db.session.commit()
    return hosts