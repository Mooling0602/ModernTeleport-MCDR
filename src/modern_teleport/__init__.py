"""Entrypoint of ModernTeleport.

About docstring and i18n, see [CODESTYLE.md](doc/CODESTYLE.md).
"""

from mcdreforged import PluginServerInterface

import modern_teleport.runtime as rt
from modern_teleport.config import load_config
from modern_teleport.config.i18n import tr
from modern_teleport.rcon import connect_rcon


def on_load(server: PluginServerInterface, _):
    rt.psi = server
    rt.config = load_config(server)
    server.logger.info(tr(server, "loading_message"))


async def on_server_startup(server: PluginServerInterface, _):
    if server.is_rcon_running():
        await connect_rcon(
            server
        )  # start async connection when sync connection is working
    server.logger.info(tr(server, "started_message"))


def on_unload(server: PluginServerInterface, _):
    server.logger.info(tr(server, "unloaded_message"))
