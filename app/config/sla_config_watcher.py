from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from app.config.sla_config import SLAConfig

from dotenv import load_dotenv

import os
import threading

load_dotenv()
sla_config_path = os.getenv("SLA_CONFIG_PATH")
if sla_config_path is None:
    raise RuntimeError("SLA config path is not set.")

class SLAConfigWatcher(FileSystemEventHandler):
    def on_modified(self, event): # type: ignore
        if event.src_path.endswith(sla_config_path): # type: ignore
            print(vars(event))
            print("[WATCH] SLA config changed. Reloading...")
            SLAConfig.load_config()

def start_config_watcher():
    observer = Observer()
    observer.schedule(SLAConfigWatcher(), path=".", recursive=False)
    observer_thread = threading.Thread(target=observer.start)
    observer_thread.daemon = True
    observer_thread.start()
