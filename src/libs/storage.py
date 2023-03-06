# Copyright (c) 2022-2029 S2N National Lab @ CNIT (https://github.com/s2n-cnit/scms)
# author: Alex Carrega <alessandro.carrega@unige.it>

from __future__ import annotations

import logging
from typing import Dict, Optional

import yaml
from fastapi import HTTPException
from pydantic import BaseModel, ValidationError

from libs.reloader import Reloader

log = logging.getLogger(__name__)


class Storage():
    def __init__(self: Storage, path: str) -> None:
        self.path = path
        self.load()

    def load(self: Storage) -> None:
        try:
            with open(self.path, "r") as file:
                self.data = yaml.load(file, Loader=yaml.SafeLoader)
        except FileNotFoundError as not_found_err:
            raise HTTPException(status_code=404,
                                detail=f"File {self.path} not found") \
                from not_found_err

    def get(self: Storage, key: str,
            default: Optional[any] = None) -> Dict:
        return self.data.get(key, default)

    def get_model(self: Storage, model: BaseModel, key: str,
                  default: Optional[any] = None) -> BaseModel:
        try:
            return model(**self.get(key, default))
        except ValidationError as val_err:
            raise HTTPException(status_code=404,
                                detail=val_err.errors()) from val_err

    def root(self) -> Dict:
        return self.data


settings = Storage("config/settings.yaml")
