# Copyright (c) 2022-2029 TNT-Lab (https://github.com/s2n-cnit/scms)
# author: Alex Carrega <alessandro.carrega@unige.it>

from __future__ import annotations

from enum import Enum
from typing import Dict

from fastapi import APIRouter
from pydantic import BaseModel, Field

from libs.base import Base

router = APIRouter()


class Relationship(str, Enum):
    child = "child"
    parent = "parent"
    sibling = "sibling"


class Chains(Base):
    class Id(str, Enum, metaclass=Base.IdMeta):
        pass

    label: str = "chain"
    storage_path: str = "config/chains.yaml"

    class InputModel(BaseModel):
        uri: str = Field(example="http://localhost:8080",
                         description="URI of the chain node",
                         required=True)
        relationship: Relationship = Field(example=Relationship.child,
                                           description="Relationship of "
                                           "the chain node", required=True)

    class OutputModel(InputModel):
        pass

Chains.setup()

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
