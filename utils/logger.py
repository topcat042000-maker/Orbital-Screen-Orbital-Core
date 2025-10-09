import os
from datetime import datetime

LOG_PATH = "logs/"

def log(message, level="INFO"):
    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] [{level}] {message}\n"

    with open(os.path.join(LOG_PATH, "trace.log"), "a", encoding="utf-8") as f:
        f.write(entry)

    return entry.strip()
