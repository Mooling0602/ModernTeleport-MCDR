import modern_teleport.runtime as runtime

from mcdreforged.api.all import (
    PluginServerInterface,
    ServerInterface,
    Info,
    # new_thread,
    # spam_proof,
)

from modern_teleport.mcdr.config import (
    CommandNodes,
    get_command_nodes,
    get_config,
    MainConfig,
)
from modern_teleport.mcdr.commands import load_command_nodes, register_commands
from modern_teleport.modules import init_modules

psi: PluginServerInterface | None = None
try:
    psi = ServerInterface.psi()
except RuntimeError:
    psi = None


def on_load(s: PluginServerInterface, _):
    s.logger.info("Init message.")
    config: MainConfig = get_config(s)
    runtime.load_config(config)
    runtime.set_server(s)
    command_nodes: CommandNodes = get_command_nodes(s)
    load_command_nodes(command_nodes)
    register_commands(s)
    init_modules()


def on_player_joined(server: PluginServerInterface, player: str, info: Info):
    pass


def on_player_left(server: PluginServerInterface, player: str):
    pass


def on_unload(server: PluginServerInterface):
    if runtime.async_tp_mgr:
        runtime.async_tp_mgr.cancel_all_requests()
