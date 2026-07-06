from mcdreforged.api.all import (
    CommandContext,  # noqa: F401
    CommandSource,  # noqa: F401
    Literal,
    PluginServerInterface,
    SimpleCommandBuilder,
)

# These are root command literal string nodes, can be modified from configurations.
_cmd_root_pfx = "!!"
_cmd_root_node = "mtp"
_cmd_tp_back_node = "back"
_cmd_tp_home_node = "home"
_cmd_tp_manager_node = "tpm"
_cmd_tp_manager_node_alias = "tp"
_cmd_tp_request_node = "tpa"
_cmd_tp_invite_node = "tph"
_cmd_tp_warp_node = "warp"

builder = SimpleCommandBuilder()
mtp = Literal(_cmd_root_pfx + _cmd_root_node)
"""Main entrypoint for the command system of ModernTeleport.
"""


def get_namespace_pfx() -> str:
    """Get the namespace prefix of ModernTeleport, which is used to identify commands when conflicting with other plugins.

    :return: The namespace prefix string.
    """
    return "modern_teleport:"


def command_register(server: PluginServerInterface):
    raise NotImplementedError
