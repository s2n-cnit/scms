# Copyright (c) 2022-2029 S2N National Lab @ CNIT (https://github.com/s2n-cnit/scms)
# author: Alex Carrega <alessandro.carrega@unige.it>

from functools import partial

from fastapi import FastAPI

from about import description, title, version
from libs.base import Base
from libs.console import header
from libs.reloader import Reloader
from libs.storage import settings
from routers.chains import router as chains_router
from routers.commands import router as commands_router
from routers.configurations import router as configurations_router
from routers.parameters import router as parameters_router

app = FastAPI(
    debug=settings.get("debug", False),
    title=title,
    version=version,
    description=description,
    on_startup=[header, partial(Reloader.start, path="config")],
    on_shutdown=[Reloader.stop]
)

app.include_router(commands_router)
app.include_router(configurations_router)
app.include_router(parameters_router)
app.include_router(chains_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.get('host', '0.0.0.0'),
                port=settings.get('port', 9999),
                reload=settings.get('reload', True),
                workers=settings.get('workers', 5),
                log_level=settings.get('log-level', 'info'),
                log_config="config/log.yaml")
