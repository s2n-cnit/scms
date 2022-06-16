from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Callable, Dict, List, Optional, Type, TypeVar

from aenum import extend_enum
from fastapi import HTTPException
from pydantic import BaseModel

from src.libs.settings import settings

T = TypeVar("T", bound="Base")


class Base:
    class ActionModel(BaseModel):
        error: bool
        stdout: List[str]
        stderr: List[str]
        returncode: int
        start: datetime
        end: datetime

    class Model(BaseModel):
        # history: Optional[List[Base.ActionModel]]
        pass

    @classmethod
    def load(cls):
        if cls.path not in settings:
            raise HTTPException(
                status_code=404,
                details=f"{cls.label.title} (path: {cls.path} not found")
        data = settings.get(cls.path, {})
        for id in data:
            data[id].history = []
        return data

    @ classmethod
    def init(cls: Type[T]) -> None:
        cls.InputModel.update_forward_refs()
        cls.OutputModel.update_forward_refs()
        for id in cls.load():
            extend_enum(cls.Id, id, id)

    @ classmethod
    def get(cls: Type[T], id: T.Id) -> T.SettingModel:
        data = cls.load()
        if id not in data:
            raise HTTPException(status_code=404,
                                detail=f"{cls.label.title()} {id} not found")
        return data.get(id)

    @ classmethod
    def add(cls: Type[T], id: str, data: Dict[T.ActionModel]) -> None:
        data = cls.load()
        if "history" not in data[id]:
            data[id]["history"] = []
        data[id]["history"].append(data)

    @ staticmethod
    def process(data: str) -> List[str]:
        try:
            __process = map(lambda item: item.strip(), data.split("\n"))
            return list(filter(lambda item: item, __process))
        except Exception:
            return []

    @ classmethod
    def action(
        cls: Type[T], id: T.Id, callback: Callable,
        **callback_kwargs: Dict[any, any]
    ) -> T.ActionModel:
        start = datetime.now()
        res = callback(cls.get(id), **callback_kwargs)
        end = datetime.now()
        data = cls.ActionModel(
            error=res.returncode is not None and res.returncode > 0,
            stdout=cls.process(res.stdout),
            stderr=cls.process(res.stderr),
            returncode=res.returncode or 0,
            start=start,
            end=end,
        )
        cls.add(id, data)
        return data


class Format(str, Enum):
    yaml = "yaml"
    json = "json"
