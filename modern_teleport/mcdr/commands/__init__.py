# pyright: reportCallIssue=false
import os
import modern_teleport.runtime as runtime

from mcdreforged.api.all import (
    CommandContext,
    PluginServerInterface,
    ServerInterface,
    CommandSource,
    SimpleCommandBuilder,
    Text,
    Boolean,
    CommandSyntaxError,
)
from location_api import MCPosition, Point3D
from modern_teleport.modules import GetInfo
from modern_teleport.modules.tpmanager import (
    TeleportToAny,
    TeleportAsk,
    TeleportBetweenPlayers,
)
from modern_teleport.utils import Player, ExecSource
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
    _tpa: str = command_nodes.teleport_ask
    _tpr: str = command_nodes.teleport
    _cmd: str = _pfx + _plg
    s.logger.info("register_commands")
    builder.arg("player", Text).suggests(
        lambda: GetInfo.get_online_list() or []
    )
    builder.arg("target", Text).suggests(
        lambda: GetInfo.get_online_list() or []
    )
    builder.arg("to_pos", Boolean)
    build_commands(
        builder,
        [
            f"{_cmd} delete config",
            f"{_cmd} delete config.main",
            f"{_cmd} config reset",
            f"{_cmd} config reset main",
            f"{_cmd} delete config.main --reload",
            f"{_cmd} config reset main --reload",
        ],
        on_plugin_clean_main_config,
    )

    builder.command(
        f"{_pfx}{_plg} debug select <player>",
        _debug_on_select_player
    )
    builder.command(f"{_pfx}{_plg} debug player <player>", Player.on_debug)
    builder.command(
        f"{_pfx}{_plg} debug online",
        lambda src: GetInfo.list_online_players(src)
    )
    builder.command(
        f"{_pfx}{_plg} debug locate <player>",
        _debug_on_locate_player
    )
    build_commands(
        builder,
        [
            f"{_pfx}{_plg} debug teleport <to_pos>",
            f"{_pfx}{_plg} debug teleport <to_pos> <player>",
        ],
        _debug_on_teleport_player,
    )
    build_commands(
        builder,
        [
            f"{_pfx}{_tpa} <player> <target>",
            f"{_pfx}{_tpa} <player>"
        ],
        _testing_tpa_command
    )
    build_commands(
        builder,
        [
            f"{_pfx}{_tpr} accept",
            f"{_pfx}{_tpr} accept <target>"
        ],
        _testing_tpr_accept_command
    )
    builder.register(s)


def _testing_tpa_command(src: CommandSource, ctx: CommandContext):
    target: str | None = ctx.get("target", None)
    player: str | None = ctx.get("player")
    source_player: str | None = None  # pyright: ignore[reportRedeclaration, reportAssignmentType] # noqa: E501
    if not player:
        raise CommandSyntaxError("failed to parse argument `player`.")
    if not GetInfo.is_player_online(player):
        src.reply("player_offline")
        return
    if target:
        if not src.has_permission_higher_than(3):
            src.reply("permission_denied")
            return
        if not GetInfo.is_player_online(target):
            src.reply("player_offline")
            return
        tpa_request: TeleportBetweenPlayers = TeleportAsk(
            ExecSource("player", target)
        )
        tpa_request.set_target(player)
    else:
        if src.is_player:
            source_player = src.player  # pyright: ignore[reportAttributeAccessIssue] # noqa: E501
        else:
            src.reply("missing_argument_target")
            return
        tpa_request: TeleportBetweenPlayers = TeleportAsk(
            ExecSource("player", source_player)
        )
        tpa_request.set_target(player)
    if runtime.tp_mgr:
        runtime.tp_mgr += tpa_request
    src.reply("tpa.create_request")


def _testing_tpr_accept_command(src: CommandSource, ctx: CommandContext):
    target: str | None = ctx.get("target", None)
    if target:
        if not GetInfo.is_player_online(target):
            src.reply("player_offline")
            return
        if not src.has_permission_higher_than(3):
            src.reply("permission_denied")
            return
        if runtime.tp_mgr:
            runtime.tp_mgr.find_run_task(target)
    else:
        if not src.is_player:
            src.reply("missing_augument_target")
            return
        player: str = src.player  # pyright: ignore[reportAttributeAccessIssue] # noqa: E501
        if runtime.tp_mgr:
            runtime.tp_mgr.find_run_task(player)


def _debug_on_select_player(src: CommandSource, ctx: CommandContext):
    player: str | None = ctx.get("player", None)
    if player:
        src.reply(f"Choosing {player}")


def _debug_on_locate_player(src: CommandSource, ctx: CommandContext):
    player: str | None = ctx.get("player", None)
    if player:
        position: MCPosition | None = GetInfo.get_player_position(player)
        if position:
            src.reply(f"Position: {str(position.point)}")
            src.reply(f"Dimension: {position.dimension}")
        else:
            src.reply("Failed to locate player.")


def _debug_on_teleport_player(src: CommandSource, ctx: CommandContext):
    teleport: TeleportToAny | None = None
    player: str | None = ctx.get("player", None)
    target: str | MCPosition = "Bot"
    if ctx.get("to_pos", False):
        target = MCPosition(Point3D(12, 64, 35), "minecraft:overworld")
    if src.is_console:
        teleport = TeleportToAny(ExecSource("console"))
        teleport.set_target(target, player)
    elif src.is_player:
        player = src.player  # pyright: ignore[reportAttributeAccessIssue]
        teleport = TeleportToAny(ExecSource("player", player))
        teleport.set_target(target)
    else:
        src.reply("Not implemented yet.")
        return
    command: str | None = teleport.execute(debug=True)
    if command:
        src.reply(command)


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
    _main_dir: str = server.get_data_folder()
    os.remove(os.path.join(_main_dir, __config_path))
    server.logger.info("reset.file_removed")
    if "--reload" in ctx.command:
        server.reload_plugin(server.get_self_metadata().id)
