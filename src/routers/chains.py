# Copyright (c) 2020-2029 GUARD Project (https://www.guard-project.eu)
# author: Alex Carrega <alessandro.carrega@cnit.it>

from __future__ import annotations

from enum import Enum
from typing import Dict

from fastapi import APIRouter
from pydantic import Field

from src.libs.base import Base

router = APIRouter()


class Relationship(str, Enum):
    child = "child"
    parent = "parent"
    sibling = "sibling"


class Chains(Base):
    class Id(str, Enum):
        pass

    label = "chain"
    path = "chains"

    class InputModel(Base.Model):
        uri: str = Field(example="http://localhost:8080",
                         description="URI of the chain node",
                         required=True)
        relationship: Relationship = Field(example=Relationship.child,
                                           description="Relationship of "
                                           "the chain node", required=True)

    class OutputModel(InputModel):
        pass


Chains.init()


@router.get("/chains",
            description="List all available chains settings",
            response_model=Dict[Chains.Id, Chains.OutputModel])
def get() -> Dict[Chains.Id, Chains.OutputModel]:
    return {chain: get_record(chain) for chain in Chains.Id}


@ router.get("/chains/{id}",
             description="Get the chain settings",
             response_model=Chains.OutputModel)
def get_record(id: Chains.Id) -> Chains.OutputModel:
    return Chains.get(id)
