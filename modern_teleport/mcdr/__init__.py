from mcdreforged.api.all import (
    PluginServerInterface,
    ServerInterface,
    new_thread,
    spam_proof,
)

from modern_teleport.mcdr.config import CommandNodes, get_command_nodes, get_config, MainConfig
from modern_teleport.mcdr.commands import load_command_nodes, register_commands

psi = ServerInterface.psi()
config: MainConfig | None = None


def on_load(s: PluginServerInterface, prev_module):
    global config
    s.logger.info("Init message.")
    config = get_config(s)
    command_nodes: CommandNodes = get_command_nodes(s)
    load_command_nodes(command_nodes)
    register_commands(s)
