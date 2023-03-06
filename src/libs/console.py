# Copyright (c) 2022-2029 S2N National Lab @ CNIT (https://github.com/s2n-cnit/scms)
# author: Alex Carrega <alessandro.carrega@unige.it>

import logging

from rich import pretty, traceback  # noqa: E402
from rich.console import Console  # noqa: E402
from rich.panel import Panel  # noqa: E402

from about import description, title, version
from libs.storage import settings

pretty.install()
traceback.install(show_locals=settings.get("debug", False))

log = logging.getLogger(__name__)


def header() -> None:
    ident: str = f"{title} v:{version}"
    console = Console()
    console.print(Panel.fit(ident))
    log.info(description)
