from mcdreforged.api.all import PluginServerInterface

from modern_teleport.config.data import MTPConfig


def get_config(server: PluginServerInterface) -> MTPConfig:
    config = server.load_config_simple(
        file_name="config.yml", target_class=MTPConfig
    )
    if not isinstance(config, MTPConfig):
        server.logger.error("tr#config_fallback_error")
        raise RuntimeWarning(
            "Failed to load valid config options for 'modern_teleport', will fallback to default values."
        )
    return config
