# Copyright (c) 2022-2029 S2N National Lab @ CNIT (https://github.com/s2n-cnit/scms)
# author: Alex Carrega <alessandro.carrega@unige.it>

from libs.reloader import Reloader
from libs.storage import Storage

parameters = Storage("config/parameters.yaml")

Reloader.start(path='config', join_observer=True)
