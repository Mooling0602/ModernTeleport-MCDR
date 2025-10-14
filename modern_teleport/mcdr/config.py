import os

from typing import Literal, Any
from mcdreforged.api.all import Serializable, PluginServerInterface

__command_nodes_path = "command_nodes.yml"
__config_path = "config.yml"
__auto_enabled_location_marker_as_warp: bool = False


class CommandNodes(Serializable):
    prefix: str = "!!"
    plugin: str = "mtp"
    back: str = "back"
    home: str = "home"
    teleport: str = "tpr"
    teleport_ask: str = "tpa"
    teleport_invite: str = "tph"
    warp: str = "warp"


class PluginModules(Serializable):
    back: bool = False
    home: bool = True
    teleport: bool = True
    teleport_ask: bool = True
    teleport_invite: bool = True
    warp: bool = True


class DataStorage(Serializable):
    save_to_world: bool = False
    server_dir: str = ""
    world_name: str = "world"


class OptionalAPIs(Serializable):
    online_player_api: bool = False
    minecraft_data_api: bool = False


class TimeoutManager(Serializable):
    rcon_wait: float = 0.5
    rcon_failed: float = 5
    teleport: float = 120


class MainConfig(Serializable):
    enable: bool = False
    enable_modules: PluginModules = PluginModules()
    identity_mode: Literal["name", "uuid"] = "name"
    rcon_support: bool = False
    rcon_module: Literal["mcdr", "async_rcon"] = "mcdr"
    rcon_feedback: bool = True
    timeout: TimeoutManager = TimeoutManager()
    location_marker_as_warp: bool = False
    optional_apis: OptionalAPIs = OptionalAPIs()
    data_storage: DataStorage = DataStorage()


def get_main_config_folder(s: PluginServerInterface) -> str:
    return s.get_data_folder()


def get_default_config() -> MainConfig:
    return MainConfig()


def get_command_nodes(s: PluginServerInterface) -> CommandNodes:
    try:
        _command_nodes = s.load_config_simple(
            file_name=__command_nodes_path,
            target_class=CommandNodes,
            echo_in_console=False,
        )
        s.logger.info("config.load_command_nodes")
    except Exception as e:
        s.logger.error(
            f"Error loading customed command nodes, fallback to default: {e}"
        )
        return CommandNodes()
    assert isinstance(_command_nodes, CommandNodes)
    return _command_nodes


def get_config(s: PluginServerInterface) -> MainConfig:
    global __auto_enabled_location_marker_as_warp
    _config: Any | None = None
    _main_dir = get_main_config_folder(s)
    _config_path = os.path.join(_main_dir, __config_path)
    _mcdr_config = s.get_mcdr_config()
    _server_dir: str | None = _mcdr_config.get("working_directory", None)
    _detected_async_rcon: bool = False
    if os.path.exists(_config_path):
        s.logger.info("config.load_existing")
        try:
            _config = s.load_config_simple(
                file_name=__config_path,
                target_class=MainConfig,
            )
        except Exception as e:
            s.logger.error("Error loading main config: ")
            raise e
    if isinstance(_config, MainConfig):
        s.logger.info("config.success")
        return _config
    s.logger.info("config.generate")
    _new_config: MainConfig = get_default_config()
    s.logger.info("config.auto_detect")
    _plugins: list[str] = s.get_plugin_list()
    if "mg_events" in _plugins:
        s.logger.info("optional.mg_events")
        _new_config.enable_modules.back = True
    if "async_rcon" in _plugins:
        s.logger.info("optional.async_rcon")
        _new_config.rcon_support = True
        _new_config.rcon_module = "async_rcon"
        _detected_async_rcon = True
    if "location_marker" in _plugins:
        s.logger.info("optional.location_marker")
        _new_config.location_marker_as_warp = True
        __auto_enabled_location_marker_as_warp = True
    if s.is_server_startup() and s.is_rcon_running():
        if not _detected_async_rcon:
            s.logger.info("rcon.mcdr")
            _new_config.rcon_support = True
    else:
        if "online_player_api" in _plugins:
            s.logger.info("optional.online_player_api")
            _new_config.optional_apis.online_player_api = True
        if "minecraft_data_api" in _plugins:
            s.logger.info("optional.minecraft_data_api")
            _new_config.optional_apis.minecraft_data_api = True
    s.logger.info("config.detected")
    _world_dir: str | None = None
    if _server_dir:
        _world_dir = os.path.join(
            _server_dir,
            _new_config.data_storage.world_name
        )
    if _world_dir and os.path.exists(_world_dir):
        s.logger.info("config.world_detected")
        _new_config.data_storage.save_to_world = True
    try:
        s.save_config_simple(
            config=_new_config,
            file_name=__config_path,
            in_data_folder=True,
        )
    except Exception as e:
        s.logger.error(f"Error saving new config: {e}")
        s.logger.info("config.fallback")
        return get_default_config()
    s.logger.info("config.success")
    return _new_config
