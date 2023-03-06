# Copyright (c) 2022-2029 TNT-Lab (https://github.com/s2n-cnit/scms)
# author: Alex Carrega <alessandro.carrega@unige.it>

from __future__ import annotations

import json
from ast import Param
from enum import Enum
from functools import partial
from subprocess import CompletedProcess
from typing import Any, Callable, Dict, List

import yaml
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from libs.base import Base, Format

router = APIRouter()


class Parameters(Base):
    class Id(str, Enum, metaclass=Base.IdMeta):
        pass

    label: str = "parameter"
    storage_path: str = "config/parameters.yaml"
    loader: Dict[Format, Callable] = {Format.yaml:
                                      partial(yaml.load,
                                              Loader=yaml.SafeLoader),
                                      Format.json: json.load}
    dumper: Dict[Format, Callable] = {Format.yaml: yaml.dump,
                                      Format.json: json.dump}

    class InputModel(BaseModel):
        source: str
        format: Format
        xpath: List[str]

    class OutputModel(InputModel):
        value: Any
        not_found: bool


Parameters.setup()


@router.get("/parameters",
            description="List all available parameter settings",
            response_model=Dict[Parameters.Id, Parameters.OutputModel])
def get() -> Dict[Parameters.Id, Parameters.OutputModel]:
    return {param: get_record(param) for param in Parameters.Id}


@router.get("/parameters/{id}",
            description="Get the parameter settings",
            response_model=Parameters.OutputModel)
def get_record(id: Parameters.Id) -> Parameters.OutputModel:
    param: Parameters.InputModel = Parameters.get(id)
    value = read(param)
    return Parameters.OutputModel(**param.dict(), value=value, not_found=value is None)


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
        write(parameter, value)
        return CompletedProcess([], returncode=0, stdout="", stderr="")
    return Parameters.action(id, __set, value=value)


def read(param: Parameters.InputModel) -> any:
    try:
        with open(param.source, "r") as file:
            loader: Callable = Parameters.loader[param.format]
            content = loader(file)
            value = content
            for x in param.xpath:
                value = value.get(x, {})
            if value == {}: value = None
            return value
    except FileNotFoundError as not_found_err:
        raise HTTPException(status_code=404,
                            detail=f"File {param.source} not found") from not_found_err


def write(param: Parameters.InputModel, value: any) -> None:
    try:
        with open(param.source, "r") as file:
            loader: Callable = Parameters.loader[param.format]
            content = loader(file)
            dest = content
            for x in param.xpath[:-1]:
                dest = dest[x]
            dest[param.xpath[-1]] = value
        with open(param.source, "w") as file:
            dumper: Callable = Parameters.dumper[param.format]
            dumper(content, file)
    except FileNotFoundError as not_found_err:
        raise HTTPException(status_code=404,
                            detail=f"File {param.source} not found") from not_found_err
