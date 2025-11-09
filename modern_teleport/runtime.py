from mcdreforged.api.all import PluginServerInterface
from location_api import MCPosition
from modern_teleport.mcdr.config import MainConfig
from modern_teleport.utils import Player
from modern_teleport.modules.rcon import RconManager
from modern_teleport.modules.storage import DataManager
from modern_teleport.modules.tpmanager_async import SessionManager

# Initial
config: MainConfig | None = None
server: PluginServerInterface | None = None

# Working modules
rcon: RconManager | None = None
data_mgr: DataManager | None = None
async_tp_mgr: SessionManager | None = None
rcon_online_players: list[Player] | None = None

# Cached player data
latest_death_positions: dict[str, MCPosition] = {}


def load_config(cfg: MainConfig):
    """Load plugin config in `modern_teleport.runtime`.

    Args:
        cfg (MainConfig): Valid plugin config instance.
    """
    global config
    config = cfg


def set_server(s: PluginServerInterface):
    """Set MCDReforged plugin server interface.

    Args:
        s (PluginServerInterface): MCDReforged plugin server interface.
    """
    global server
    server = s
