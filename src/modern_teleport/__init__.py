"""Entrypoint of ModernTeleport.

About docstring and i18n, see [CODESTYLE.md](doc/CODESTYLE.md).
"""

from mcdreforged.api.all import PluginServerInterface

from modern_teleport.utils import tr


def on_load(server: PluginServerInterface, _):
    server.logger.info(tr(server, "loading_message"))


def on_unload(server: PluginServerInterface, _):
    server.logger.info(tr(server, "unloaded_message"))
