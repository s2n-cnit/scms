# Copyright (c) 2022-2029 TNT-Lab (https://github.com/tnt-lab-unige-cnit/scms)
# author: Alex Carrega <alessandro.carrega@unige.it>

from dynaconf import Dynaconf
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

from libs.log import log


class Settings:
    path = '.'
    files = ["settings.yaml", ".secrets.yaml"]

    def __init__(self):
        self.load()
        self.event_handler = PatternMatchingEventHandler(patterns=self.files)
        self.event_handler.on_any_event = self.on_any_event

        self.observer = Observer()
        self.observer.schedule(self.event_handler, self.path, recursive=False)
        self.observer.start()

    def load(self):
        self.data = Dynaconf(settings_files=self.files)

    def on_any_event(self, event):
        log.warning("Settings file changed, reloading...")
        self.load()


settings = Settings().data
