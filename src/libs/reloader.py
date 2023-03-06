from __future__ import annotations

import logging
import os
from typing import Dict, Type

from watchdog.events import FileModifiedEvent, PatternMatchingEventHandler
from watchdog.observers import Observer

log = logging.getLogger(__name__)


class Reloader:
    router_klasses: Dict[str, any] = {}

    @classmethod
    def add_router_klass(cls: Type[Reloader], pattern: str,
                         router_klass: any) -> None:
        cls.router_klasses[pattern] = router_klass

    @classmethod
    def start(cls: Type[Reloader], path: str, join_observer: bool = False) -> None:
        for klass in cls.router_klasses.values():
            klass.init()
        event_handler = PatternMatchingEventHandler(patterns=cls.router_klasses.keys())
        event_handler.on_modified = cls.on_modified
        cls.observer = Observer()
        cls.observer.schedule(event_handler, path, recursive=False)
        cls.observer.start()
        cls.path = path
        log.info(f"Reload on {path}")
        if join_observer:
            cls.observer.join()

    @ classmethod
    def stop(cls: Type[Reloader]):
        log.info(f"Stop reloader on {cls.path}")
        cls.observer.stop()

    @ classmethod
    def on_modified(cls: Type[Reloader], event: FileModifiedEvent) -> None:
        key: str = event.src_path.replace(f'{os.getcwd()}/', '')
        log.warning(f"File {key} changed, reloading...")
        router_klass = cls.router_klasses[key]
        router_klass.init()
        router_klass.storage.load()
