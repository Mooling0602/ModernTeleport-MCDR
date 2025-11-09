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
from modern_teleport.modules.tpmanager_async import (
    TeleportRequest,
    TeleportPosition,
)
from modern_teleport.utils import Player, tr
from modern_teleport.mcdr.config import CommandNodes, __config_path
from modern_teleport.mcdr.commands.utils import (
    build_exec_with_multiple_commands as build_commands,
    auto_get_player_from_src as get_player,
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
            f"{_cmd} config reset",
            f"{_cmd} config reset --reload",
            f"{_cmd} config reset main",
            f"{_cmd} config reset main --reload",
        ],
        on_plugin_clean_main_config,
    )
    builder.command(f"{_cmd} debug player <player>", Player.on_debug_command)
    builder.command(
        f"{_cmd} debug online",
        lambda src: GetInfo.list_online_players(src),
    )
    builder.command(f"{_cmd} debug locate <player>", _debug_on_locate_player)
    build_commands(
        builder,
        [f"{_cmd} debug query death", f"{_cmd} debug query death <player>"],
        _debug_on_query_player_death,
    )
    build_commands(
        builder,
        [
            f"{_cmd} debug teleport",
            f"{_cmd} debug teleport <player>",
        ],
        _debug_on_teleport_player,
    )
    build_commands(
        builder,
        [
            f"{_pfx}{_tpa} <player>",
            f"{_pfx}{_tpa} <player> --debug",
            f"{_pfx}{_tpa} <player> <target>",
            f"{_pfx}{_tpa} <player> <target> --debug",
        ],
        _testing_async_tpa_command,
    )
    build_commands(
        builder,
        [
            f"{_pfx}{_tpr} accept",
            f"{_pfx}{_tpr} accept <target>",
            f"{_pfx}{_tpr} reject",
            f"{_pfx}{_tpr} reject <target>",
            f"{_pfx}{_tpr} cancel",
            f"{_pfx}{_tpr} cancel <target>",
        ],
        _testing_async_tpr_command,
    )
    builder.register(s)


def get_player_names(
    src: CommandSource, ctx: CommandContext
) -> tuple[str, str | None]:
    selected_player: str | None = ctx.get("player", None)
    if not selected_player:
        raise CommandSyntaxError("failed to parse argument `player`.")
    target_player: str | None = ctx.get("target", None)
    return selected_player, target_player


async def _testing_async_tpa_command(src: CommandSource, ctx: CommandContext):
    if not runtime.async_tp_mgr:
        src.reply("AsyncSessionManager is not running...")
        return
    selected_player, target_player = get_player_names(src, ctx)
    if not target_player:
        target_player = selected_player
        if not src.is_player:
            src.reply("missing_argument_target")
            return
        selected_player = src.player  # pyright: ignore[reportAttributeAccessIssue] # noqa: E501
    request = TeleportRequest(
        get_psi(src),
        "ask",
        selected_player,
        target_player,
    )
    if not GetInfo.is_player_online(
        selected_player
    ) or not GetInfo.is_player_online(target_player):
        if "--debug" not in ctx.command:
            src.reply("player_not_online")
            return
        src.reply(f"> {request.command}")
        return
    runtime.async_tp_mgr.schedule_add(request)


async def _testing_async_tpr_command(src: CommandSource, ctx: CommandContext):
    if not runtime.async_tp_mgr:
        src.reply("AsyncSessionManager is not running...")
        return
    _target_player: str | None = ctx.get("target", None)
    if not _target_player:
        if not src.is_player:
            src.reply("missing_argument_target")
            return
        target_player: str = src.player  # pyright: ignore[reportAttributeAccessIssue, reportRedeclaration] # noqa: E501
    else:
        target_player: str = _target_player
    # if not GetInfo.is_player_online(target_player):
    #     src.reply("player_not_online")
    #     return
    if "accept" in ctx.command:
        runtime.async_tp_mgr.confirm_latest_request(
            target_player,
            "accept",
        )
    elif "reject" in ctx.command:
        runtime.async_tp_mgr.confirm_latest_request(
            target_player,
            "reject",
        )
    elif "cancel" in ctx.command:
        runtime.async_tp_mgr.confirm_latest_request(
            target_player,
            "cancel",
        )
    else:
        raise CommandSyntaxError("failed to parse a valid option.")


def _testing_tpa_command(src: CommandSource, ctx: CommandContext):
    target: str | None = ctx.get("target", None)
    player: str | None = ctx.get("player", None)
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
        tpa_request: TeleportBetweenPlayers = TeleportAsk(  # pyright: ignore[reportRedeclaration] # noqa: E501
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


def _debug_on_query_player_death(src: CommandSource, ctx: CommandContext):
    player = get_player(src, ctx)
    if player:
        death_position: MCPosition | None = runtime.latest_death_positions.get(
            player, None
        )
        if not death_position:
            src.reply("query.no_results")
            return
        src.reply(
            f"latest_death_position: {death_position.dimension}: "
            f"{death_position.point}"
        )


def _debug_on_teleport_player(src: CommandSource, ctx: CommandContext):
    server: PluginServerInterface = src.get_server().psi()
    teleport: TeleportPosition = TeleportPosition(server)
    teleport.set_position(Point3D(12, 64, 35))
    player: str | None = ctx.get("player", None)
    if src.is_console:
        if not player:
            src.reply("command.missing_argument.player")
            return
        teleport.set_target(player)
        teleport.execute(debug=True)
    elif src.is_player:
        teleport.set_target(src.player)  # pyright: ignore[reportAttributeAccessIssue] # noqa: E501
        teleport.execute(debug=True, src_player=src.player)  # pyright: ignore[reportAttributeAccessIssue] # noqa: E501
    else:
        src.reply(tr(server, "feature.not_implemented"))
        return


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
