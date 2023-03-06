from __future__ import annotations

from datetime import datetime
from enum import Enum, EnumMeta
from typing import Callable, Dict, List, Type

from aenum import extend_enum
from fastapi import HTTPException
from pydantic import BaseModel

from libs.reloader import Reloader
from libs.storage import Storage


class Base:
    class IdMeta(EnumMeta):
        def __contains__(cls, item):
            return item in [v.value for v in cls.__members__.values()]

    class ActionModel(BaseModel):
        error: bool
        stdout: List[str]
        stderr: List[str]
        returncode: int
        start: datetime
        end: datetime

    @classmethod
    def init(cls: Type[Base]) -> None:
        for id in cls.Id:
            if id not in cls.storage.root().keys():
                cls.Id.__dict__['_member_names_'].remove(id.name)
        for id in cls.storage.root().keys():
            if id not in cls.Id:
                extend_enum(cls.Id, id, id)

    @classmethod
    def setup(cls: Type[Base]) -> None:
        cls.storage = Storage(cls.storage_path)
        cls.InputModel.update_forward_refs()
        cls.OutputModel.update_forward_refs()
        Reloader.add_router_klass(cls.storage_path, cls)

    @classmethod
    def get(cls: Type[Base], id: Base.Id) -> BaseModel:
        if id not in cls.storage.root():
            raise HTTPException(status_code=404,
                                detail=f"{cls.label.title()} {id} not found")
        return cls.storage.get_model(cls.InputModel, id.name)

    @staticmethod
    def process(data: str) -> List[str]:
        try:
            __process = map(lambda item: item.strip(), data.split("\n"))
            return list(filter(lambda item: item, __process))
        except Exception:
            return []

    @classmethod
    def action(
        cls: Type[Base], id: Base.Id, task: Callable,
        **task_kwargs: Dict[any, any]
    ) -> Base.ActionModel:
        start = datetime.now()
        res = task(cls.get(id), **task_kwargs)
        end = datetime.now()
        return cls.ActionModel(
            error=res.returncode is not None and res.returncode > 0,
            stdout=cls.process(res.stdout),
            stderr=cls.process(res.stderr),
            returncode=res.returncode or 0,
            start=start,
            end=end,
        )


class Format(str, Enum):
    yaml = "yaml"
    json = "json"
    property = "ini"
