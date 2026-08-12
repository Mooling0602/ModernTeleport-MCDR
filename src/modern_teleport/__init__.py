"""Entrypoint of ModernTeleport.

About docstring and i18n, see [CODESTYLE.md](doc/CODESTYLE.md).
"""

from mcdreforged.api.all import PluginServerInterface

import modern_teleport.runtime as rt
from modern_teleport.config import get_config
from modern_teleport.config.i18n import tr


def on_load(server: PluginServerInterface, _):
    rt.psi = server
    rt.config = get_config(server)
    server.logger.info(tr(server, "loading_message"))


def on_unload(server: PluginServerInterface, _):
    server.logger.info(tr(server, "unloaded_message"))
