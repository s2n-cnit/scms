# Copyright (c) 2020-2029 GUARD Project (https://www.guard-project.eu)
# author: Alex Carrega <alessandro.carrega@cnit.it>

from __future__ import annotations

import json
from enum import Enum
from subprocess import CompletedProcess
from typing import Any, Callable, Dict
from urllib import response

import yaml
from fastapi import APIRouter
from pydantic import BaseModel, Field
from this import d

from src.libs.base import Base, Format

router = APIRouter()


class Configurations(Base):
    class Id(str, Enum):
        pass

    label = "configuration"
    path = "configurations"

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


Configurations.init()


@router.get("/configurations",
            description="List all available configuration settings",
            response_model=Dict[Configurations.Id, Configurations.OutputModel])
def get() -> Dict[Configurations.Id, Configurations.OutputModel]:
    return {
        configuration: get_record(configuration) for configuration in Configurations.Id
    }


@router.get("/configurations/{id}",
            description="Get the configuration settings",
            response_model=Configurations.OutputModel)
def get_record(id: Configurations.Id) -> Configurations.OutputModel:
    data = Configurations.get(id)
    read(data, format=Format.yaml, loader=yaml.load)
    read(data, format=Format.json, loader=json.load)
    return data


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
    def __set(configuration: Configurations.Id,
              content: Any) -> CompletedProcess[str]:
        write(configuration, content, format=Format.yaml, dumper=yaml.dump)
        write(configuration, content, format=Format.json, dumper=json.dump)
        return CompletedProcess([], returncode=0, stdout="", stderr="")

    return Configurations.action(id, __set, content=content)


def read(data: Configurations.InputModel,
         format: Format, loader: Callable) -> None:
    if data.format == format:
        with open(data.path, "r") as file:
            data.update(content=loader(file))


def write(
    data: Configurations.InputModel, content: Any,
    format: Format, dumper: Callable
) -> None:
    if data.format == format:
        with open(data.path, "w") as file:
            dumper(content, file)
