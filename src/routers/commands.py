# Copyright (c) 2022-2029 S2N National Lab @ CNIT (https://github.com/s2n-cnit/scms)
# author: Alex Carrega <alessandro.carrega@unige.it>

from __future__ import annotations

from enum import Enum
from functools import partial
from subprocess import PIPE, CompletedProcess, Popen, run
from typing import Callable, Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from libs.base import Base

router = APIRouter()


class Commands(Base):
    class Id(str, Enum, metaclass=Base.IdMeta):
        pass

    label: str = "command"
    storage_path: str = "config/commands.yaml"

    class InputModel(BaseModel):
        script: str = Field(example="ls", description="Command to execute")
        daemon: Optional[bool] = Field(example=True,
                                       description='Indicate if the command '
                                       'has to be executed as daemon',
                                       default=False)

    class OutputModel(InputModel):
        pass


Commands.setup()


@router.get("/commands",
            description="List all available command settings",
            response_model=Dict[Commands.Id, Commands.OutputModel])
def get() -> Dict[Commands.Id, Commands.OutputModel]:
    return {command: get_record(command) for command in Commands.Id}


@router.get("/commands/{id}",
            description="Get the command settings",
            response_model=Commands.OutputModel)
def get_record(id: Commands.Id) -> Commands.OutputModel:
    cmd: Commands.InputModel = Commands.get(id)
    return Commands.OutputModel(**cmd.dict())


@router.post("/commands",
             description="Execute a set of commands",
             response_model=Dict[Commands.Id, Commands.OutputModel])
def set() -> Dict[Commands.Id, Commands.ActionModel]:
    return {command: set_record(command) for command in Commands.Id}


@router.post("/commands/{id}",
             description="Execute a command",
             response_model=Commands.ActionModel)
def set_record(id: Commands.Id) -> Commands.ActionModel:
    def __set(command: Commands.InputModel) -> CompletedProcess[str] | Popen:
        fn: Callable = Popen if command.daemon else run
        call_fn: Callable = partial(fn, shell=True, stdout=PIPE, stderr=PIPE)
        add_args = dict(start_new_session=True) if command.daemon \
            else dict(universal_newlines=True)
        return call_fn(**add_args)
    return Commands.action(id, __set)
