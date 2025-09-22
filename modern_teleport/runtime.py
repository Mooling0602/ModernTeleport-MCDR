from mcdreforged.api.all import PluginServerInterface

from modern_teleport.mcdr.config import MainConfig

config: MainConfig | None = None
server: PluginServerInterface | None = None


def load_config(cfg: MainConfig):
    global config
    config = cfg


def set_server(s: PluginServerInterface):
    global server
    server = s
