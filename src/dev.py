
from ntpath import join

from libs.reloader import Reloader
from libs.storage import Storage

parameters = Storage("config/parameters.yaml")

Reloader.start(path='config', join_observer=True)
    