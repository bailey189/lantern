def run_discovery_scan(subnet):
    return {"status": "discovery scan complete", "subnet": subnet}

def run_masscan(subnet):
    return {"status": "port scan complete", "subnet": subnet}

def run_arp_scan():
    return {"status": "arp scan complete"}

def run_nikto():
    return {"status": "web scan complete"}