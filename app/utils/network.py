import netifaces
import ipaddress

def get_host_network():
    """
    Returns the host's primary subnet in CIDR notation, e.g., '192.168.1.0/24'.
    Returns None if it cannot be determined.
    """
    try:
        gws = netifaces.gateways()
        default_iface = gws['default'][netifaces.AF_INET][1]
        iface_info = netifaces.ifaddresses(default_iface)[netifaces.AF_INET][0]
        ip = iface_info['addr']
        netmask = iface_info['netmask']
        network = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False)
        return str(network)
    except Exception:
        return None