# Copyright (c) 2022-2029 TNT-Lab (https://github.com/tnt-lab-unige-cnit/scms)
# author: Alex Carrega <alessandro.carrega@unige.it>

from rich import pretty, traceback  # noqa: E402
from rich.console import Console  # noqa: E402
from rich.panel import Panel  # noqa: E402

from about import version
from libs.log import log
from libs.settings import settings

pretty.install()
traceback.install(show_locals=settings.get("debug", False))


def header() -> None:
    ident: str = f"{settings.project} - {settings.title} v:{version}"
    console = Console()
    console.print(Panel.fit(ident))
    log.info(settings.description)
