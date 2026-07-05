"""Entrypoint of ModernTeleport.

About docstring and i18n, see [CODESTYLE.md](doc/CODESTYLE.md).
"""

from mcdreforged.api.all import PluginServerInterface


def on_load(server: PluginServerInterface, _):
    server.logger.info("i18n.loading_message")
