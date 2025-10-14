import modern_teleport.runtime as runtime

from mcdreforged.api.all import PluginServerInterface
from modern_teleport.utils.execute_if import execute_if


class WarpManager:
    def __init__(self) -> None:
        pass


class WarpShare:
    def __init__(self) -> None:
        pass


class WarpForLoc:
    """Use [LocationMarker](https://github.com/TISUnion/LocationMarker) as \
    public waypoints manager.
    """
    @execute_if(
        lambda:
        runtime.config is not None
        and runtime.config.enable_modules.warp is True
        and runtime.config.location_marker_as_warp is True,
        True
    )
    def __init__(self, server: PluginServerInterface):
        assert runtime.config is not None
        self.server: PluginServerInterface = server
        self.s = self.server
