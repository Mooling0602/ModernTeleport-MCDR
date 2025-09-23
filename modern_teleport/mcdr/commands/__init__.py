import os

from mcdreforged.api.all import (
    CommandContext,
    PluginServerInterface,
    ServerInterface,
    CommandSource,
    SimpleCommandBuilder,
    Text,
)

from modern_teleport.mcdr.config import CommandNodes, __config_path
from modern_teleport.mcdr.commands.utils import (
    build_exec_with_multiple_commands as build_commands,
)

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
    if psi:
        return psi
    else:
        raise RuntimeError("error.need_mcdr_server")


def register_commands(s: PluginServerInterface):
    # builder.register(s)
    if not command_nodes or not builder:
        return
    _pfx: str = command_nodes.prefix
    _plg: str = command_nodes.plugin
    _cmd: str = _pfx + _plg
    s.logger.info("register_commands")
    build_commands(
        builder,
        [
            f"{_cmd} delete config.main",
            f"{_cmd} config reset main",
            f"{_cmd} delete config.main --reload",
            f"{_cmd} config reset main --reload",
        ],
        on_plugin_clean_main_config,
    )
    builder.arg("player", Text).suggests(lambda: ["Steve", "Alex"])
    builder.command(f"{_pfx}{_plg} debug select <player>", _debug_on_select_player)
    builder.register(s)


def _debug_on_select_player(src: CommandSource, ctx: CommandContext):
    player: str | None = ctx.get("player", None)
    if player:
        src.reply(f"Choosing {player}")


def on_plugin_clean_main_config(src: CommandSource, ctx: CommandContext):
    if not src.has_permission(4):
        src.reply("permission.denied")
        return
    server: PluginServerInterface = get_psi(src)
    global __remove_main_config
    if not __remove_main_config:
        server.logger.warning("reset.confirm.config.main")
        __remove_main_config = True
        return
    _main_dir = server.get_data_folder()
    os.remove(os.path.join(_main_dir, __config_path))
    server.logger.info("reset.file_removed")
    if "--reload" in ctx.command:
        server.reload_plugin(server.get_self_metadata().id)
