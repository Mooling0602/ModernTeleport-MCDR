import modern_teleport.runtime as runtime

from mcdreforged.api.all import (
    PluginServerInterface,
    CommandSource,
    new_thread,
)
from auto_uuid_api import is_uuid, local_api
from location_api import Point3D, MCPosition
from modern_teleport.utils import Player, execute_if
from modern_teleport.modules.rcon import RconManager
from modern_teleport.modules.storage import DataManager
from modern_teleport.modules.tpmanager_async import AsyncSessionManager


@execute_if(
    lambda: runtime.config is not None and runtime.server is not None, True
)
def init_modules():
    assert runtime.server is not None
    runtime.rcon = RconManager(runtime.server)
    runtime.data_mgr = DataManager(runtime.server)
    runtime.async_tp_mgr = AsyncSessionManager(runtime.server)
    runtime.server.logger.info("modules.initialized")


@execute_if(
    lambda: runtime.server is not None and runtime.config is not None, True
)
def init_online_players(s: PluginServerInterface):
    _online_players = GetInfo.get_online_list()
    online_players: list[Player] = []
    if _online_players:
        for i in _online_players:
            uuid: str | None = local_api.get(i)
            if not uuid:
                raise ValueError(f"uuid not found for {i}")
            player = Player(i, uuid)
            online_players.append(player)
    runtime.rcon_online_players = online_players


@execute_if(
    lambda: runtime.config is not None
    and runtime.config.optional_apis.online_player_api
)
def get_online_players_optional(s: PluginServerInterface) -> list[str] | None:
    oapi = s.get_plugin_instance("online_player_api")  # type: ignore
    if oapi:
        return oapi.get_player_list()  # type: ignore


@execute_if(
    lambda: runtime.config is not None
    and runtime.config.optional_apis.minecraft_data_api
)
def get_player_pos_optional(
    s: PluginServerInterface, player: str
) -> MCPosition | None:
    mc_data_api = s.get_plugin_instance("minecraft_data_api")  # type: ignore
    if mc_data_api:  # type: ignore
        # fmt: off
        position: list | None = mc_data_api.get_player_info(
            player, "Pos",
        )  # type: ignore
        dimension: str | None = mc_data_api.get_player_info(
            player, "Dimension"
        )  # type: ignore
        # fmt: off
        if position and dimension:
            return MCPosition(Point3D(*position), dimension)


class GetInfo:
    def __init__(self):
        pass

    @classmethod  # pyright: ignore[reportArgumentType]
    @new_thread("MTPRcon: get_online_players")
    @execute_if(lambda: runtime.server is not None, True)
    def list_online_players(cls, src: CommandSource):
        assert runtime.server is not None
        players: list[str] | None = cls.get_online_list()
        if players:
            src.reply("-----Online Players-----")
            for i in players:
                src.reply(f"- {i}")
        else:
            src.reply("No online players.")

    @classmethod
    @execute_if(lambda: runtime.server is not None, True)
    def get_online_list(cls) -> list[str]:
        assert runtime.server is not None
        result: list[str] | None = get_online_players_optional(runtime.server)
        if not result:
            if runtime.rcon:
                result = runtime.rcon.get_online_players()
        return result if result is not None else []

    @classmethod
    @execute_if(lambda: runtime.server is not None, True)
    def is_player_online(cls, player: str) -> bool:
        assert runtime.server is not None
        _player: str | None = player
        if is_uuid(player):
            _player = local_api.get(player)
        if _player:
            online_players: list[str] | None = get_online_players_optional(
                runtime.server
            )
            if not online_players:
                if runtime.rcon:
                    online_players = runtime.rcon.get_online_players()
                return (_player in online_players) if online_players else False
        return False

    @classmethod
    @execute_if(lambda: runtime.server is not None, True)
    def get_player_position(cls, player: str) -> MCPosition | None:
        assert runtime.server is not None
        position: MCPosition | None = get_player_pos_optional(
            runtime.server, player
        )
        if not position:
            if runtime.rcon:
                position = runtime.rcon.get_player_pos(player)
        return position


if __name__ == "__main__":
    print("Core module of MTP(modern_teleport).")
