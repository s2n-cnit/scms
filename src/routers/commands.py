# Copyright (c) 2022-2029 TNT-Lab (https://github.com/tnt-lab-unige-cnit/scms)
# author: Alex Carrega <alessandro.carrega@unige.it>

from __future__ import annotations

from enum import Enum
from subprocess import PIPE, CompletedProcess, Popen, run
from typing import Dict, Optional

from fastapi import APIRouter
from pydantic import Field

from libs.base import Base

router = APIRouter()


class Commands(Base):
    class Id(str, Enum):
        pass

    label = "command"
    path = "commands"

    class InputModel(Base.Model):
        script: str = Field(example="ls", description="Command to execute")
        daemon: Optional[bool] = Field(example=True,
                                       description='Indicate if the command '
                                       'has to be executed as daemon',
                                       default=False)

    class OutputModel(InputModel):
        pass


Commands.init()


@router.get("/commands",
            description="List all available command settings",
            response_model=Dict[Commands.Id, Commands.OutputModel])
def get() -> Dict[Commands.Id, Commands.OutputModel]:
    return {command: get_record(command) for command in Commands.Id}


@router.get("/commands/{id}",
            description="Get the command settings",
            response_model=Commands.OutputModel)
def get_record(id: Commands.Id) -> Commands.OutputModel:
    return Commands.get(id)


@router.post("/commands",
             description="Execute a set of commands",
             response_model=Dict[Commands.Id, Commands.OutputModel])
def set() -> Dict[Commands.Id, Commands.ActionModel]:
    return {command: set_record(command) for command in Commands.Id}


@router.post("/commands/{id}",
             description="Execute a command",
             response_model=Commands.ActionModel)
def set_record(id: Commands.Id) -> Commands.ActionModel:
    def __set_record(command: Commands.InputModel) \
            -> CompletedProcess[str] | Popen:
        return Popen(command.script, shell=True, stdout=PIPE, stderr=PIPE,
                     start_new_session=True) \
            if command.get("daemon", False) else \
            run(command.script, check=False, shell=True,
                stdout=PIPE, stderr=PIPE, universal_newlines=True)
    return Commands.action(id, __set_record)
