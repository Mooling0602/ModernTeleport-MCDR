import modern_teleport.runtime as runtime

from mcdreforged.api.all import PluginServerInterface

from location_api import MCPosition, Point3D
from modern_teleport.utils import ExecSourceType, ExecSource, execute_if


class SessionManager:
    pass


class TeleportToAny:
    @execute_if(lambda: runtime.server is not None, True)
    def __init__(self, source: ExecSource | None = None):
        assert runtime.server is not None
        self.source_type: ExecSourceType | None = None
        self.source_name: str | None = None
        if source:
            self.source_type = source.source_type
            self.source_name = source.source_name
        self.server: PluginServerInterface = runtime.server
        self.target: MCPosition | str | None = None
        self.player: str | None = None

    def set_source(self, source: ExecSource):
        self.source_type = source.source_type
        self.source_name = source.source_name

    def set_target(self, target: MCPosition | str, player: str | None = None):
        self.target = target
        if self.source_type == "console":
            if player:
                self.player = player

    @staticmethod
    def get_string_pos(point: Point3D) -> str:
        return f"{point.x} {point.y} {point.z}"

    @staticmethod
    def get_tp_command_with_mcposition(position: MCPosition, player: str):
        pos_str = TeleportToAny.get_string_pos(position.point)
        return f"execute in {position.dimension} run tp {player} {pos_str}"

    @execute_if(
        lambda: runtime.server is not None and runtime.config is not None
    )
    def execute(self, debug: bool = False) -> None | str:
        s: PluginServerInterface = self.server
        player: str | None = None
        command: str | None = None
        if not self.source_type:
            raise TypeError("source_type is not specified.")
        if not self.target:
            raise ValueError("target is not set.")
        if self.source_type == "console":
            if not self.player:
                raise ValueError("player is not specified.")
            player = self.player
        elif self.source_type == "player":
            if not self.source_name:
                raise TypeError("player name is unknown.")
            player = self.source_name
        else:
            raise NotImplementedError(
                'only "console" or "player" is supported.'
            )
        if isinstance(self.target, MCPosition):
            command = TeleportToAny.get_tp_command_with_mcposition(
                self.target, player
            )
        else:
            command = f"tp {player} {self.target}"
        if command:
            if not debug:
                s.execute(command)
            else:
                return f"> {command}"
