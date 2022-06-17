# Copyright (c) 2022-2029 TNT-Lab (https://github.com/tnt-lab-unige-cnit/scms)
# author: Alex Carrega <alessandro.carrega@unige.it>

from fastapi import FastAPI

from about import version
from libs.console import header
from libs.settings import settings
from routers.chains import router as chains_router
from routers.commands import router as commands_router
from routers.configurations import router as configurations_router
from routers.parameters import router as parameters_router

app = FastAPI(
    debug=settings.get("debug", False),
    title=settings.title,
    version=version,
    description=settings.description,
)

app.include_router(commands_router)
app.include_router(configurations_router)
app.include_router(parameters_router)
app.include_router(chains_router)


if __name__ == "__main__":
    header()
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=settings.port,
                reload=True, workers=settings.workers,
                log_level=settings.get('log-level', 'info'))
