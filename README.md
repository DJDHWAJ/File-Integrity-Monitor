# File Integrity Monitor (FIM)

## **Objective**
The **File Integrity Monitor (FIM)** is a security tool designed to **detect unauthorized changes** in critical system files. This tool helps security teams monitor file integrity in **real-time**, ensuring compliance with security best practices and regulatory requirements.

## **How It Works**
1. **Creates a baseline of file hashes (SHA256).**
2. **Monitors the filesystem for changes (additions, deletions, modifications).**
3. **Compares current file hashes with the baseline to detect anomalies.**
4. **Logs detected changes and generates alerts.**
5. **Optional: Sends email notifications for unauthorized modifications.**

## **Use Cases**
- **Detect unauthorized file modifications (Ransomware, Insider Threats).**
- **Ensure compliance with PCI DSS, HIPAA, and SOC 2.**
- **Monitor critical system files on Linux and Windows.**
- **Prevent tampering with log files or security configurations.**

## **Installation**
```bash
pip install -r requirements.txt
