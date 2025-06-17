from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from app.config.sla_config import SLAConfig
from app.config.settings import settings

import threading

class SLAConfigWatcher(FileSystemEventHandler):
    def on_modified(self, event): # type: ignore
        if event.src_path.endswith(settings.SLA_CONFIG_PATH): # type: ignore
            print(vars(event))
            print("[WATCH] SLA config changed. Reloading...")
            SLAConfig.load_config()

def start_config_watcher():
    observer = Observer()
    observer.schedule(SLAConfigWatcher(), path=".", recursive=False)
    observer_thread = threading.Thread(target=observer.start)
    observer_thread.daemon = True
    observer_thread.start()
