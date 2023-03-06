# Copyright (c) 2022-2029 S2N National Lab @ CNIT (https://github.com/s2n-cnit/scms)
# author: Alex Carrega <alessandro.carrega@unige.it>

from __future__ import annotations

import json
from enum import Enum
from functools import partial
from subprocess import CompletedProcess
from typing import Any, Callable, Dict

import yaml
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from libs.base import Base, Format

router = APIRouter()


class Configurations(Base):
    class Id(str, Enum, metaclass=Base.IdMeta):
        pass

    label: str = "configuration"
    storage_path: str = "config/configurations.yaml"
    loader: Dict[Format, Callable] = {Format.yaml:
                                      partial(yaml.load,
                                              Loader=yaml.SafeLoader),
                                      Format.json: json.load}
    dumper: Dict[Format, Callable] = {Format.yaml: yaml.dump,
                                      Format.json: json.dump}

    class InputModel(BaseModel):
        path: str = Field(example="tests/test.json",
                          description="Path of the configuration file",
                          required=True)
        format: Format = Field(example=Format.json,
                               description="Format of the configuration file",
                               required=True)

    class OutputModel(InputModel):
        content: Any = Field(example="c: 1",
                             description="Content of the configuration file",
                             required=True)


Configurations.setup()


@router.get("/configurations",
            description="List all available configuration settings",
            response_model=Dict[Configurations.Id, Configurations.OutputModel])
def get() -> Dict[Configurations.Id, Configurations.OutputModel]:
    return {cfg: get_record(cfg) for cfg in Configurations.Id}


@router.get("/configurations/{id}",
            description="Get the configuration settings",
            response_model=Configurations.OutputModel)
def get_record(id: Configurations.Id) -> Configurations.OutputModel:
    cfg: Configurations.InputModel = Configurations.get(id)
    content = read(cfg)
    return Configurations.OutputModel(**cfg.dict(), content=content)


@router.post("/configurations",
             description="Update a set of configurations",
             response_model=Dict[Configurations.Id,
                                 Configurations.ActionModel])
def set(
    data: Dict[Configurations.Id, Any],
) -> Dict[Configurations.Id, Configurations.ActionModel]:
    return {id: set_record(id, content) for id, content in data.items()}


@router.post("/configurations/{id}",
             description="Update a configuration",
             response_model=Configurations.ActionModel)
def set_record(
    id: Configurations.Id, content: Dict[Any, Any]
) -> Configurations.ActionModel:
    def __set(cfg: Configurations.Id,
              content: Any) -> CompletedProcess[str]:
        write(cfg, content)
        return CompletedProcess([], returncode=0, stdout="", stderr="")

    return Configurations.action(id, __set, content=content)


def read(cfg: Configurations.InputModel) -> any:
    try:
        with open(cfg.path, "r") as file:
            loader: Callable = Configurations.loader[cfg.format]
            return loader(file)
    except FileNotFoundError as not_found_err:
        raise HTTPException(status_code=404,
                            detail=f"File {cfg.path} not found") from not_found_err


def write(cfg: Configurations.InputModel, content: Any) -> None:
    try:
        with open(cfg.path, "w") as file:
            dumper: Callable = Configurations.dumper[cfg.format]
            dumper(content, file)
    except FileNotFoundError as not_found_err:
        raise HTTPException(status_code=404,
                            detail=f"File {cfg.path} not found") from not_found_err
