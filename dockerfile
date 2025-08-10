FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy project files
COPY . /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y \
    nmap arp-scan \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Run any setup scripts if needed
RUN chmod +x setup.sh install_tools.sh && ./setup.sh && ./install_tools.sh

# Expose port if Lantern runs a web server (change if needed)
EXPOSE 5000

# Set the default command
CMD ["python", "run.py"]