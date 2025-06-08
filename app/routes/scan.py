import subprocess
from datetime import datetime
from flask import Blueprint, render_template, request, flash
from app import db
from app.models import Scan, ScanResult

main = Blueprint('main', __name__)

@main.route('/scan', methods=['GET', 'POST'])
def scan():
    result = None

    if request.method == 'POST':
        selected_tools = request.form.getlist('tools')
        outputs = []

        for tool in selected_tools:
            target = None
            output = None

            if tool == 'nmap':
                target = request.form.get('nmap_target')
                if target:
                    cmd = ['nmap', '-sS', target]
                    try:
                        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=60)
                    except Exception as e:
                        output = f"Nmap error: {e}"
                else:
                    output = "Nmap selected but no target specified."

            elif tool == 'masscan':
                target = request.form.get('masscan_target')
                if target:
                    parts = target.split(':')
                    ip_part = parts[0]
                    ports = parts[1] if len(parts) > 1 else '1-65535'
                    cmd = ['masscan', ip_part, '-p', ports, '--rate', '1000']
                    try:
                        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=60)
                    except Exception as e:
                        output = f"Masscan error: {e}"
                else:
                    output = "Masscan selected but no target specified."

            # Add other tools similarly...

            else:
                output = f"Tool {tool} not implemented or requires external execution."

            # Save scan + result to DB if we have output
            if output:
                new_scan = Scan(tool_name=tool, target=target, started_at=datetime.utcnow())
                db.session.add(new_scan)
                db.session.commit()  # commit now to get scan id

                new_result = ScanResult(scan_id=new_scan.id, output=output)
                db.session.add(new_result)

                # Mark scan finished
                new_scan.finished_at = datetime.utcnow()
                db.session.commit()

                outputs.append(f"--- Results for {tool} on target {target or 'N/A'} ---\n{output}")

        result = "\n\n".join(outputs)
        flash("Scans completed and saved to database.", "success")

    return render_template('scan.html', result=result)
