import os
import shutil

LOG_PATH = "logs/"
CACHE_PATH = "cache/"

def remove_logs():
    if os.path.exists(LOG_PATH):
        for file in os.listdir(LOG_PATH):
            path = os.path.join(LOG_PATH, file)
            if os.path.isfile(path):
                os.remove(path)
        return "Logs removed"
    return "No logs found"

def remove_cache():
    if os.path.exists(CACHE_PATH):
        shutil.rmtree(CACHE_PATH)
        os.makedirs(CACHE_PATH)
        return "Cache cleared"
    return "No cache found"
