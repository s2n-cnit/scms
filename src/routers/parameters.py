# Copyright (c) 2022-2029 TNT-Lab (https://github.com/tnt-lab-unige-cnit/scms)
# author: Alex Carrega <alessandro.carrega@unige.it>

from __future__ import annotations

import json
from enum import Enum
from pydoc import describe
from subprocess import CompletedProcess
from typing import Any, Callable, Dict, List

import yaml
from fastapi import APIRouter

from libs.base import Base, Format

router = APIRouter()


class Parameters(Base):
    class Id(str, Enum):
        pass

    label = "parameter"
    path = "parameters"

    class InputModel(Base.Model):
        source: str
        format: Format
        xpath: List[str]

    class OutputModel(InputModel):
        value: Any


Parameters.init()


@router.get("/parameters",
            description="List all available parameter settings",
            response_model=Dict[Parameters.Id, Parameters.OutputModel])
def get() -> Dict[Parameters.Id, Parameters.OutputModel]:
    return {parameter: get_record(parameter) for parameter in Parameters.Id}


@router.get("/parameters/{id}",
            description="Get the parameter settings",
            response_model=Parameters.OutputModel)
def get_record(id: Parameters.Id) -> Parameters.OutputModel:
    parameter = Parameters.get(id)
    read(parameter, format=Format.yaml, loader=yaml.load)
    read(parameter, format=Format.json, loader=json.load)
    return parameter


@router.post("/parameters",
             description="Update a set of parameters",
             response_model=Dict[Parameters.Id, Parameters.OutputModel])
def set(data: Dict[Parameters.Id, Any]) -> Dict[Parameters.Id,
                                                Parameters.ActionModel]:
    return {id: set_record(id, value) for id, value in data.items()}


@router.post("/parameters/{id}",
             description="Update a parameter",
             response_model=Parameters.ActionModel)
def set_record(id: Parameters.Id,
               value: Dict[Any, Any]) -> Parameters.ActionModel:
    return set_record_inline(id, value)


@router.post("/parameters/{id}/{value}",
             description="Update a parameter",
             response_model=Parameters.ActionModel)
def set_record_inline(id: Parameters.Id, value: Any) -> Parameters.ActionModel:
    def __set(parameter: Parameters.InputModel,
              value: Any) -> CompletedProcess[str]:
        write(parameter, value, format=Format.yaml, loader=yaml.load,
              dumper=yaml.dump)
        write(parameter, value, format=Format.json, loader=json.load,
              dumper=json.dump)
        return CompletedProcess([], returncode=0, stdout="", stderr="")

    return Parameters.action(id, __set, value=value)


def read(data: Parameters.InputModel, format: Format,
         loader: Callable) -> None:
    if data.format == format:
        with open(data.source, "r") as file:
            content = loader(file)
            value = content
            for x in data.xpath:
                value = value[x]
        data.update(value=value)


def write(data: Parameters.InputModel, value: any, format: Format,
          loader: Callable, dumper: Callable) -> None:
    if data.format == format:
        read(data, format=format, loader=loader)
        with open(data.source, "r") as file:
            content = loader(file)
            dest = content
            for x in data.xpath[:-1]:
                dest = dest[x]
            dest[data.xpath[-1]] = value
        with open(data.source, "w") as file:
            dumper(content, file)
