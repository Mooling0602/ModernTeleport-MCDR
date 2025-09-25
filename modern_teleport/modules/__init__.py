import modern_teleport.runtime as runtime

from mcdreforged.api.all import PluginServerInterface
from auto_uuid_api import is_uuid, local_api
from location_api import Point3D, MCPosition
from modern_teleport.utils import execute_if
from modern_teleport.modules.rcon import RconManager
from modern_teleport.modules.storage import DataManager

rcon: RconManager | None = None
data_mgr: DataManager | None = None


@execute_if(lambda: runtime.config is not None and runtime.server is not None)
def init_modules():
    global rcon, data_mgr
    rcon = RconManager()
    data_mgr = DataManager()


@execute_if(
    lambda: runtime.config is not None
    and runtime.config.optional_apis.online_player_api
)
def get_online_players(s: PluginServerInterface) -> list[str] | None:
    oapi = s.get_plugin_instance("online_player_api")  # type: ignore
    if oapi:
        return oapi.get_player_list()  # type: ignore


@execute_if(
    lambda: runtime.config is not None
    and runtime.config.optional_apis.minecraft_data_api
)
def get_player_pos(s: PluginServerInterface, player: str) -> MCPosition | None:
    mc_data_api = s.get_plugin_instance("minecraft_data_api")  # type: ignore
    if mc_data_api:  # type: ignore
        position: list | None = mc_data_api.get_player_info(player, "Pos")  # type: ignore
        dimension: str | None = mc_data_api.get_player_info(player, "Dimension")  # type: ignore
        if position and dimension:
            return MCPosition(Point3D(*position), dimension)


class GetInfo:
    def __init__(self) -> None:
        pass

    @classmethod
    @execute_if(lambda: runtime.server is not None)
    def get_online_list(cls) -> list[str]:
        assert runtime.server is not None
        result = get_online_players(runtime.server)
        if not result:
            if rcon:
                result = rcon.get_online_players()
        return result if result is not None else []

    @classmethod
    @execute_if(lambda: runtime.server is not None)
    def is_player_online(cls, player: str) -> bool:  # pyright: ignore[reportRedeclaration]
        assert runtime.server is not None
        if is_uuid(player):
            player: str | None = local_api.get(player)
        if player:
            online_players: list[str] | None = get_online_players(runtime.server)
            if not online_players:
                if rcon:
                    online_players = rcon.get_online_players()
                return player in online_players if online_players else False
        return False


if __name__ == "__main__":
    print("This is the core module of MTP(modern_teleport).")
