from modern_teleport.mcdr.config import MainConfig

config: MainConfig | None = None


def load_config(cfg: MainConfig):
    global config
    config = cfg
