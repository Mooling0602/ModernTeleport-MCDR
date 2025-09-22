import os

from mcdreforged.api.all import (
    PluginServerInterface,
    ServerInterface,
    CommandSource,
    CommandContext,
    SimpleCommandBuilder
)

from modern_teleport.mcdr.config import CommandNodes, __config_path

builder: SimpleCommandBuilder | None = SimpleCommandBuilder()
psi: PluginServerInterface | None = None
try:
    psi = ServerInterface.psi()
except RuntimeError:
    psi = None
command_nodes: CommandNodes | None = None
__remove_main_config: bool = False


def load_command_nodes(cnodes: CommandNodes):
    global command_nodes
    command_nodes = cnodes


def get_psi(src: CommandSource | None = None) -> PluginServerInterface:
    if src:
        server: PluginServerInterface = src.get_server().psi()
        return server
    return psi


def register_commands(s: PluginServerInterface):
    # builder.register(s)
    if not command_nodes:
        return
    s.logger.info("register_commands")
    builder.command(f"{command_nodes.prefix}{
                    command_nodes.plugin} delete config.main", on_plugin_clean_main_config)
    builder.command(f"{command_nodes.prefix}{
                    command_nodes.plugin} config reset main", on_plugin_clean_main_config)
    builder.register(s)


def on_plugin_clean_main_config(src: CommandSource, ctx: CommandContext):
    if not src.has_permission(4):
        src.reply("permission.denied")
        return
    server = get_psi(src)
    global __remove_main_config
    if not __remove_main_config:
        server.logger.warning("reset.confirm.config.main")
        __remove_main_config = True
        return
    _main_dir = server.get_data_folder()
    os.remove(os.path.join(_main_dir, __config_path))
    server.logger.info("reset.file_removed")
