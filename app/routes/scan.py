import subprocess
from flask import Blueprint, render_template, request, flash

main = Blueprint('main', __name__)

@main.route('/scan', methods=['GET', 'POST'])
def scan():
    result = None

    if request.method == 'POST':
        selected_tools = request.form.getlist('tools')
        outputs = []

        for tool in selected_tools:
            if tool == 'nmap':
                target = request.form.get('nmap_target')
                if target:
                    cmd = ['nmap', '-sS', target]
                    try:
                        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=60)
                        outputs.append(f"--- Nmap scan results for {target} ---\n{output}")
                    except Exception as e:
                        outputs.append(f"Nmap error: {e}")
                else:
                    outputs.append("Nmap selected but no target specified.")

            elif tool == 'masscan':
                target = request.form.get('masscan_target')
                if target:
                    # Example: masscan -p80 192.168.1.0/24
                    parts = target.split(':')
                    ip_part = parts[0]
                    ports = parts[1] if len(parts) > 1 else '1-65535'
                    cmd = ['masscan', ip_part, '-p', ports, '--rate', '1000']
                    try:
                        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=60)
                        outputs.append(f"--- Masscan results for {target} ---\n{output}")
                    except Exception as e:
                        outputs.append(f"Masscan error: {e}")
                else:
                    outputs.append("Masscan selected but no target specified.")

            elif tool == 'angryip':
                ip_range = request.form.get('angryip_range')
                if ip_range:
                    # AngryIPScanner is GUI, so maybe call a CLI equivalent or skip
                    outputs.append("AngryIPScanner selected but is GUI-only, skipping.")
                else:
                    outputs.append("AngryIPScanner selected but no IP range specified.")

            elif tool == 'arpscan':
                interface = request.form.get('arpscan_interface')
                if interface:
                    cmd = ['arp-scan', '--interface', interface, '--localnet']
                    try:
                        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=60)
                        outputs.append(f"--- Arp-scan results on {interface} ---\n{output}")
                    except Exception as e:
                        outputs.append(f"Arp-scan error: {e}")
                else:
                    outputs.append("Arp-scan selected but no interface specified.")

            elif tool == 'dhcpdump':
                # dhcpdump usually needs root and interface to listen on, assuming 'eth0'
                cmd = ['dhcpdump', '-i', 'eth0', '-c', '10']
                try:
                    output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=30)
                    outputs.append("--- Dhcpdump recent DHCP packets ---\n" + output)
                except Exception as e:
                    outputs.append(f"Dhcpdump error: {e}")

            elif tool == 'kismet':
                outputs.append("Kismet selected. Kismet is a passive wireless tool, run it externally.")

            elif tool == 'aircrack':
                outputs.append("Aircrack-ng selected. Requires external Wi-Fi adapter and setup; run externally.")

            elif tool == 'hping3':
                target = request.form.get('hping3_target')
                if target:
                    cmd = ['hping3', '-S', '-p', '80', '-c', '5', target]
                    try:
                        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=30)
                        outputs.append(f"--- Hping3 SYN scan to {target}:80 ---\n{output}")
                    except Exception as e:
                        outputs.append(f"Hping3 error: {e}")
                else:
                    outputs.append("Hping3 selected but no target specified.")

            elif tool == 'nikto':
                url = request.form.get('nikto_url')
                if url:
                    cmd = ['nikto', '-h', url]
                    try:
                        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=60)
                        outputs.append(f"--- Nikto scan for {url} ---\n{output}")
                    except Exception as e:
                        outputs.append(f"Nikto error: {e}")
                else:
                    outputs.append("Nikto selected but no URL specified.")

            elif tool == 'wapiti':
                url = request.form.get('wapiti_url')
                if url:
                    cmd = ['wapiti', '-u', url]
                    try:
                        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=60)
                        outputs.append(f"--- Wapiti scan for {url} ---\n{output}")
                    except Exception as e:
                        outputs.append(f"Wapiti error: {e}")
                else:
                    outputs.append("Wapiti selected but no URL specified.")

            elif tool == 'skipfish':
                url = request.form.get('skipfish_url')
                if url:
                    cmd = ['skipfish', '-o', '/tmp/skipfish-output', url]
                    outputs.append("Skipfish scan started (output in /tmp/skipfish-output).")
                else:
                    outputs.append("Skipfish selected but no URL specified.")

            elif tool == 'sqlmap':
                url = request.form.get('sqlmap_url')
                if url:
                    cmd = ['sqlmap', '-u', url, '--batch']
                    try:
                        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=120)
                        outputs.append(f"--- SQLmap scan for {url} ---\n{output}")
                    except Exception as e:
                        outputs.append(f"SQLmap error: {e}")
                else:
                    outputs.append("SQLmap selected but no URL specified.")

            elif tool == 'trivy':
                image = request.form.get('trivy_image')
                if image:
                    cmd = ['trivy', 'image', image]
                    try:
                        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=120)
                        outputs.append(f"--- Trivy scan for image {image} ---\n{output}")
                    except Exception as e:
                        outputs.append(f"Trivy error: {e}")
                else:
                    outputs.append("Trivy selected but no image specified.")

            elif tool == 'ansible':
                outputs.append("Ansible selected. Run playbooks externally or implement integration.")

            else:
                outputs.append(f"Unknown tool selected: {tool}")

        result = "\n\n".join(outputs)

        # Optionally flash success or error messages
        flash("Scans completed. See results below.", "success")

    return render_template('scan.html', result=result)
