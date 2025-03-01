import os
import hashlib
import json
import time
import logging
import smtplib
from email.mime.text import MIMEText
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure Logging
logging.basicConfig(filename="file_integrity.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Email Configuration (Optional: Uncomment & Configure)
ALERT_EMAIL = "your_email@example.com"
SMTP_SERVER = "smtp.example.com"
SMTP_PORT = 587
SMTP_USER = "your_email@example.com"
SMTP_PASS = "your_password"

# Directory to Monitor
MONITOR_DIR = "monitor_dir/"
INTEGRITY_FILE = "file_integrity.json"

# Function to compute SHA256 hash of a file
def compute_hash(file_path):
    try:
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(4096):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        logging.error(f"Error computing hash for {file_path}: {e}")
        return None

# Function to load integrity baseline
def load_integrity_baseline():
    if os.path.exists(INTEGRITY_FILE):
        with open(INTEGRITY_FILE, "r") as f:
            return json.load(f)
    return {}

# Function to save integrity baseline
def save_integrity_baseline(data):
    with open(INTEGRITY_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Function to send email alerts
def send_alert(subject, message):
    try:
        msg = MIMEText(message)
        msg["From"] = SMTP_USER
        msg["To"] = ALERT_EMAIL
        msg["Subject"] = subject

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, ALERT_EMAIL, msg.as_string())
        server.quit()

        logging.info(f"Alert sent: {subject}")
    except Exception as e:
        logging.error(f"Failed to send alert: {e}")

# Class for monitoring file system changes
class IntegrityMonitor(FileSystemEventHandler):
    def __init__(self, baseline):
        self.baseline = baseline

    def on_modified(self, event):
        if not event.is_directory:
            new_hash = compute_hash(event.src_path)
            old_hash = self.baseline.get(event.src_path)

            if old_hash and new_hash and old_hash != new_hash:
                logging.warning(f"File modified: {event.src_path}")
                send_alert("File Integrity Alert", f"File modified: {event.src_path}")
                self.baseline[event.src_path] = new_hash
                save_integrity_baseline(self.baseline)

    def on_created(self, event):
        if not event.is_directory:
            new_hash = compute_hash(event.src_path)
            if new_hash:
                logging.warning(f"New file created: {event.src_path}")
                send_alert("File Integrity Alert", f"New file created: {event.src_path}")
                self.baseline[event.src_path] = new_hash
                save_integrity_baseline(self.baseline)

    def on_deleted(self, event):
        if not event.is_directory:
            logging.warning(f"File deleted: {event.src_path}")
            send_alert("File Integrity Alert", f"File deleted: {event.src_path}")
            if event.src_path in self.baseline:
                del self.baseline[event.src_path]
                save_integrity_baseline(self.baseline)

# Function to initialize the integrity baseline
def initialize_baseline():
    logging.info("Initializing file integrity baseline...")
    baseline = {}
    for root, _, files in os.walk(MONITOR_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            baseline[file_path] = compute_hash(file_path)
    save_integrity_baseline(baseline)
    return baseline

# Main function to run the File Integrity Monitor
def run_monitor():
    if not os.path.exists(MONITOR_DIR):
        os.makedirs(MONITOR_DIR)

    baseline = load_integrity_baseline()
    if not baseline:
        baseline = initialize_baseline()

    observer = Observer()
    event_handler = IntegrityMonitor(baseline)
    observer.schedule(event_handler, MONITOR_DIR, recursive=True)
    observer.start()

    logging.info("File Integrity Monitor is running...")

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
        logging.info("File Integrity Monitor stopped.")

# Run the File Integrity Monitor
if __name__ == "__main__":
    run_monitor()
