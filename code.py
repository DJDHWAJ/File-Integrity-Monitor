import os, hashlib, json, time, logging, smtplib
from email.mime.text import MIMEText
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# log stuff
logging.basicConfig(filename="file_log.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# config (emails??)
EMAIL_TO = "your_email@example.com"
SMTP_ADDR = "smtp.example.com"
SMTP_PORT = 587
EMAIL_USER = "your_email@example.com"
EMAIL_PASS = "your_password"

# folder to check (not sure if this is the best place)
DIR_TO_WATCH = "watch_this/"
HASH_FILE = "file_data.json"

DEBUG = False  # set to True if you wanna debug

# function to get file hash (does this work??)
def getHash(fpath):
    try:
        h = hashlib.sha256()
        with open(fpath, "rb") as file:
            while chunk := file.read(4096):  
                h.update(chunk)
        return h.hexdigest()
    except FileNotFoundError:
        logging.error(f"Missing file: {fpath}")
    except Exception as e:
        logging.error(f"hash fail {fpath}: {e}")
    return None

# load stored hashes
def loadHashes():
    if os.path.exists(HASH_FILE):
        try:
            with open(HASH_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            logging.error("bad hash file, maybe corrupted?")
    return {}

# save new hashes
def saveHashes(d):
    try:
        with open(HASH_FILE, "w") as f:
            json.dump(d, f, indent=4)
    except Exception as e:
        logging.error(f"cant save hashes: {e}")

# send warning emails (if enabled)
def emailWarn(subj, msg):
    if DEBUG:
        print(f"DEBUG: Would send email - {subj}")

    try:
        em = MIMEText(msg)
        em["From"] = EMAIL_USER
        em["To"] = EMAIL_TO
        em["Subject"] = subj

        with smtplib.SMTP(SMTP_ADDR, SMTP_PORT) as srv:
            srv.starttls()
            srv.login(EMAIL_USER, EMAIL_PASS)
            srv.sendmail(EMAIL_USER, EMAIL_TO, em.as_string())

        logging.info(f"Email sent: {subj}")
    except Exception as e:
        logging.error(f"email fail: {e}")

# watch files 
class FileWatch(FileSystemEventHandler):
    def __init__(self, base):
        self.base = base

    def checkEvent(self, event, eType):
        if event.is_directory:
            return
        
        fpath = event.src_path
        newHash = getHash(fpath)

        if eType == "mod":
            oldHash = self.base.get(fpath)
            if oldHash and newHash and oldHash != newHash:
                logging.warning(f"MODIFIED!!: {fpath}")
                emailWarn("Alert: File Changed", f"mod: {fpath}")
                self.base[fpath] = newHash
                saveHashes(self.base)

        elif eType == "new" and newHash:
            logging.warning(f"NEW FILE: {fpath}")
            emailWarn("Alert: New File", f"new: {fpath}")
            self.base[fpath] = newHash
            saveHashes(self.base)

        elif eType == "gone":
            logging.warning(f"DELETED: {fpath}")
            emailWarn("Alert: File Gone", f"deleted: {fpath}")
            if fpath in self.base:
                del self.base[fpath]
                saveHashes(self.base)

    def on_modified(self, event):
        self.checkEvent(event, "mod")

    def on_created(self, event):
        self.checkEvent(event, "new")

    def on_deleted(self, event):
        self.checkEvent(event, "gone")

# first time setup (baseline)
def makeBaseline():
    logging.info("making hash baseline...")
    base = {}
    if not os.path.exists(DIR_TO_WATCH):
        logging.warning(f"umm where is '{DIR_TO_WATCH}' ?? making it now")
        os.makedirs(DIR_TO_WATCH)
    for root, _, files in os.walk(DIR_TO_WATCH):
        for f in files:
            fpath = os.path.join(root, f)
            base[fpath] = getHash(fpath)
    saveHashes(base)
    return base

# start watching
def startWatch():
    if not os.path.exists(DIR_TO_WATCH):
        os.makedirs(DIR_TO_WATCH)

    base = loadHashes()
    if not base:
        base = makeBaseline()

    obs = Observer()
    evt_handler = FileWatch(base)
    obs.schedule(evt_handler, DIR_TO_WATCH, recursive=True)
    obs.start()

    logging.info("watching now...")

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        obs.stop()
        obs.join()
        logging.info("stopped watching.")

# go
if __name__ == "__main__":
    startWatch()
