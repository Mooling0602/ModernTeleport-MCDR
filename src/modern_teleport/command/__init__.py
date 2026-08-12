from mcdreforged.api.all import (
    CommandContext,  # noqa: F401
    CommandSource,  # noqa: F401
    Literal,
    PluginServerInterface,
    SimpleCommandBuilder,
)

# Root command literal node fallbacks.
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


def command_builder(server: PluginServerInterface):
    mtp.runs(lambda src: src.reply("Not implemented yet."))


def command_register(server: PluginServerInterface):
    command_builder(server)
    server.register_command(mtp)
