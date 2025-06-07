
# Lantern

**Lantern** is an open-source, Raspberry Pi-based network reconnaissance and compliance reporting tool.  
It integrates various scanning utilities to provide comprehensive insights into network environments, making it invaluable for security assessments and compliance checks.

## Features

- **Automated Network Scanning**: Utilizes tools like Nmap, Masscan, ARP-Scan, and Nikto for thorough network analysis.
- **Web Interface**: Built with Flask, offering an intuitive UI for managing scans and viewing results.
- **Data Storage**: Employs PostgreSQL for robust and scalable data management.
- **Compliance Reporting**: Generates reports to assist in meeting various compliance standards.

---

## Installation Guide

### 1. Flash Raspberry Pi OS

- **Download Raspberry Pi OS**: Obtain the latest version from the [official website](https://www.raspberrypi.com/software/).
- **Flash the OS**: Use [Raspberry Pi Imager](https://www.raspberrypi.com/software/) to write the OS to an SD card.
- **Enable SSH**: After flashing, create an empty file named `ssh` (no extension) in the boot partition to enable SSH on first boot.

### 2. Initial Setup

- **Insert SD Card**: Place the SD card into your Raspberry Pi and power it on.
- **SSH into Raspberry Pi**:
  ```bash
  ssh pi@<raspberry_pi_ip_address>
  ```
  Replace `<raspberry_pi_ip_address>` with your Pi's IP address.

### 3. System Updates

Update the system packages:
```bash
sudo apt update && sudo apt upgrade -y
```

### 4. Install Dependencies

Install necessary packages:
```bash
sudo apt install -y python3 python3-pip python3-venv git postgresql nmap masscan arp-scan nikto
```

### 5. Clone the Lantern Repository

Clone your project repository:
```bash
git clone https://github.com/bailey189/lantern.git
cd lantern
```

### 6. Set Up Python Virtual Environment

Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 7. Install Python Dependencies

Install required Python packages:
```bash
pip install -r requirements.txt
```

### 8. Configure PostgreSQL

- **Access PostgreSQL**:
  ```bash
  sudo -u postgres psql
  ```
- **Create Database and User**:
  ```sql
  CREATE DATABASE lantern_db;
  CREATE USER lantern_user WITH PASSWORD 'securepassword';
  GRANT ALL PRIVILEGES ON DATABASE lantern_db TO lantern_user;
  \q
  ```
- **Update Configuration**: Modify your application's database configuration to match the credentials above.

### 9. Initialize the Database

Run the database migration scripts:
```bash
flask db upgrade
```

### 10. Run the Application

Start the Flask application:
```bash
python run.py
```

Or, to make it accessible from other devices:
```bash
flask run --host=0.0.0.0
```

Access the web interface by navigating to `http://<raspberry_pi_ip_address>:5000` in your browser.

---

## Usage

- **Initiate Scans**: Use the web interface to start various network scans.
- **View Results**: Access detailed scan reports and logs through the dashboard.
- **Generate Reports**: Produce compliance reports in formats like PDF or CSV.

---

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your enhancements.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

For more information or questions about the code, please refer to the project's GitHub repository: [https://github.com/bailey189/lantern](https://github.com/bailey189/lantern).
