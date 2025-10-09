from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mcdreforged.api.all import PluginServerInterface
    from modern_teleport.mcdr.config import MainConfig
    from modern_teleport.modules.rcon import RconManager
    from modern_teleport.modules.storage import DataManager
    from modern_teleport.modules.tpmanager import SessionManager

# Initial
config: MainConfig | None = None
server: PluginServerInterface | None = None

# Working modules
rcon: RconManager | None = None
data_mgr: DataManager | None = None
tp_mgr: SessionManager | None = None


def load_config(cfg: MainConfig):
    global config
    config = cfg


def set_server(s: PluginServerInterface):
    global server
    server = s
