from mcdreforged.api.all import PluginServerInterface
from modern_teleport.mcdr.config import MainConfig
from modern_teleport.utils import Player
from modern_teleport.modules.rcon import RconManager
from modern_teleport.modules.storage import DataManager
from modern_teleport.modules.tpmanager import SessionManager
from modern_teleport.modules.tpmanager_async import AsyncSessionManager

# Initial
config: MainConfig | None = None
server: PluginServerInterface | None = None

# Working modules
rcon: RconManager | None = None
data_mgr: DataManager | None = None
tp_mgr: SessionManager | None = None
async_tp_mgr: AsyncSessionManager | None = None
rcon_online_players: list[Player] | None = None


def load_config(cfg: MainConfig):
    global config
    config = cfg


def set_server(s: PluginServerInterface):
    global server
    server = s
