import modern_teleport.runtime as runtime

from mcdreforged.api.all import PluginServerInterface


class WarpManager:
    def __init__(self) -> None:
        pass


class WarpShare:
    def __init__(self) -> None:
        pass


class WarpForLoc:
    def __init__(self) -> None:
        if not runtime.config:
            raise RuntimeError("error.config_not_loaded")
        if not runtime.server:
            raise RuntimeError("error.need_mcdr_server")
        self.config: runtime.MainConfig = runtime.config
        self.server: PluginServerInterface = runtime.server
        self.enable: bool = False
        if (self.config.enable_modules.warp and
                self.config.location_marker_as_warp):
            self.enable = True
