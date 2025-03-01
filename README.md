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
```

## **Usage**
Run the File Integrity Monitor:
```bash
python file_integrity_monitor.py
```

## **Example Output**
### **File Integrity Log**
The tool logs file changes in `file_integrity.log`:
```
2023-03-01 03:34:02,897 - INFO - Initializing file integrity baseline...
2023-03-01 03:34:02,897 - INFO - File Integrity Monitor is running...
2023-03-01 03:38:06,146 - WARNING - New file created: monitor_dir/New Text Document.txt
2023-03-01 03:38:06,180 - ERROR - Failed to send alert: [Errno 11001] getaddrinfo failed
```

### **File Integrity Baseline**
A JSON-based integrity report is generated (`file_integrity.json`):
```json
{
    "monitor_dir/New Text Document.txt": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
}
```

## **Conclusion**
The **File Integrity Monitor (FIM)** successfully detected file modifications, logging them in `file_integrity.log`. The tool identified the creation of a new file (`New Text Document.txt`) and attempted to send an alert. However, an email alert failure occurred due to an invalid SMTP configuration.

This demonstrates that the FIM is **effective at real-time file integrity monitoring**, but email alert functionality should be properly configured. The system successfully generated **integrity baselines** and **tracked changes**, making it a valuable security tool for detecting unauthorized modifications in a monitored environment.

---

