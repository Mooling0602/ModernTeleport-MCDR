import modern_teleport.runtime as runtime

from mcdreforged.api.all import (
    PluginServerInterface,
    ServerInterface,
    Info,
    event_listener
    # new_thread,
    # spam_proof,
)
from location_api import MCPosition
from modern_teleport.mcdr.config import (
    CommandNodes,
    get_command_nodes,
    get_config,
    MainConfig,
)
from modern_teleport.mcdr.commands import load_command_nodes, register_commands
from modern_teleport.modules import init_modules, GetInfo
from modern_teleport.utils import execute_if, tr

psi: PluginServerInterface | None = None
try:
    psi = ServerInterface.psi()
except RuntimeError:
    psi = None


def on_load(s: PluginServerInterface, _):
    s.logger.info(tr(s, "on_load"))
    config: MainConfig = get_config(s)
    runtime.load_config(config)
    runtime.set_server(s)
    command_nodes: CommandNodes = get_command_nodes(s)
    load_command_nodes(command_nodes)
    register_commands(s)
    init_modules()


def on_player_joined(server: PluginServerInterface, player: str, info: Info):
    pass


def on_user_info(server: PluginServerInterface, info: Info):
    if info.content == "y":
        if info.is_from_console:
            info.cancel_send_to_server()
        # result: str = quick_confirm()
        # server.reply(info, result)


@event_listener("PlayerDeathEvent")
def on_player_death(
    server: PluginServerInterface,
    player: str,
    event: str,
    content: list
):
    death_position: MCPosition | None = GetInfo.get_player_position(player)
    if death_position:
        runtime.latest_death_positions.update({player: death_position})


@execute_if(lambda: runtime.async_tp_mgr is not None)
def on_player_left(server: PluginServerInterface, player: str):
    assert runtime.async_tp_mgr is not None
    for i in runtime.async_tp_mgr.tp_tasks:
        if i.target_player == player or i.selected_player == player:
            i.cancel()


def on_unload(server: PluginServerInterface):
    if runtime.async_tp_mgr:
        runtime.async_tp_mgr.cancel_all_requests()
