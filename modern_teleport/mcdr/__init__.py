import modern_teleport.runtime as runtime

from mcdreforged.api.all import (
    PluginServerInterface,
    ServerInterface,
    new_thread,
    spam_proof,
)

from modern_teleport.mcdr.config import (
    CommandNodes,
    get_command_nodes,
    get_config,
    MainConfig,
)
from modern_teleport.mcdr.commands import load_command_nodes, register_commands

psi: PluginServerInterface | None = None
try:
    psi = ServerInterface.psi()
except RuntimeError:
    psi = None


def on_load(s: PluginServerInterface, prev_module):
    s.logger.info("Init message.")
    config: MainConfig = get_config(s)
    runtime.load_config(config)
    runtime.set_server(s)
    command_nodes: CommandNodes = get_command_nodes(s)
    load_command_nodes(command_nodes)
    register_commands(s)
