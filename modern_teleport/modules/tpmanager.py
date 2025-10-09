import modern_teleport.runtime as runtime

from beartype import beartype
from datetime import datetime
from typing import Literal, Self

from mcdreforged.api.all import PluginServerInterface

from location_api import MCPosition, Point3D
from modern_teleport.utils import (
    ExecSourceType,
    ExecSource,
    execute_if,
    FeatureDisabledError,
)

TeleportType = Literal["ask", "invite", "to_any"]


class TeleportBetweenPlayers:
    def __init__(
        self, source: ExecSource,
        target: str | None = None,
        teleport_type: TeleportType = "ask"
    ):
        assert runtime.server is not None
        assert runtime.config is not None
        if not runtime.config.enable_modules.teleport:
            raise FeatureDisabledError(
                '"teleport" is not enabled in config.'
            )
        if source.source_type == "console":
            raise TypeError('source should be or bind a "player".')
        elif source.source_type != "player":
            raise NotImplementedError('only "player" source is supported now.')
        if source.source_name is None:
            raise TypeError(
                '"source_name" is invalid, please give a player name or uuid.'
            )
        self.source: str = source.source_name
        self.target: str | None = target
        self.teleport_type: TeleportType = teleport_type
        self.server: PluginServerInterface = runtime.server
        self.create_time: datetime = datetime.now()

    def __eq__(self, other: object):
        if isinstance(other, TeleportBetweenPlayers):
            conditions = [
                (other.source == self.source),
                (other.target == self.target),
                (other.teleport_type == self.teleport_type)
            ]
            for i in conditions:
                if not i:
                    return False
        return True

    @beartype
    def set_target(self, target: str):
        if target == self.target:
            self.server.logger.warning("set_same_target")
        self.target = target
        self.create_time = datetime.now()

    @beartype
    def set_teleport_type(self, teleport_type: TeleportType):
        if self.teleport_type == teleport_type:
            self.server.logger.warning("set_same_teleport_type")
        self.teleport_type = teleport_type

    @execute_if(
        lambda: runtime.server is not None and runtime.config is not None, True
    )
    def execute(self):
        assert runtime.config is not None
        current_time: datetime = datetime.now()
        interval: float = (current_time - self.create_time).total_seconds()
        if interval > runtime.config.timeout.teleport:
            if runtime.tp_mgr:
                runtime.tp_mgr -= self
            raise TimeoutError("teleport task is outdated!")
        if not self.target:
            raise ValueError(
                '"target" is not set. use `set_target` '
                'to set or change a target.'
            )
        if self.teleport_type == "ask":
            command: str = f"tp {self.source} {self.target}"
        elif self.teleport_type == "invite":
            command: str = f"tp {self.target} {self.source}"
        else:
            raise TypeError(
                'invalid teleport type, '
                'please select one between "ask" or "invite".'
            )
        if command:
            self.server.execute(command)
            if runtime.tp_mgr:
                runtime.tp_mgr -= self


class TeleportAsk(TeleportBetweenPlayers):
    @execute_if(
        lambda: runtime.server is not None and runtime.config is not None, True
    )
    def __init__(self, source: ExecSource, target: str | None = None):
        assert runtime.config is not None
        if not runtime.config.enable_modules.teleport_ask:
            raise FeatureDisabledError(
                '"teleport_ask" is not enabled in config.'
            )
        super().__init__(source, target, "ask")

    def set_teleport_type(self, teleport_type):
        raise AttributeError('"teleport_type" is confirmed.')

    @beartype
    def set_target(self, target: str):
        if runtime.server:
            runtime.server.tell(target, "tpr.notify_request")
        return super().set_target(target)


class TeleportInvite(TeleportBetweenPlayers):
    @execute_if(
        lambda: runtime.server is not None and runtime.config is not None, True
    )
    def __init__(self, source, target: str | None = None):
        assert runtime.config is not None
        if not runtime.config.enable_modules.teleport_invite:
            raise FeatureDisabledError(
                '"teleport_invite" is not enabled in config.'
            )
        super().__init__(source, target, "invite")

    def set_teleport_type(self, teleport_type):
        raise AttributeError('"teleport_type" is confirmed.')

    @beartype
    def set_target(self, target: str):
        if runtime.server:
            runtime.server.tell(target, "tph.notify_request")
        return super().set_target(target)


class SessionManager:
    @execute_if(
        lambda: runtime.server is not None and runtime.config is not None, True
    )
    def __init__(self):
        assert runtime.config is not None
        if not runtime.config.enable_modules.teleport:
            raise FeatureDisabledError(
                '"teleport" is not enabled in config.'
            )
        self.teleport_tasks: list[TeleportBetweenPlayers] = []

    def append(self, teleport_task: TeleportBetweenPlayers):
        self.teleport_tasks.append(teleport_task)

    def __iadd__(self, teleport_task: TeleportBetweenPlayers) -> Self:
        if teleport_task not in self.teleport_tasks:
            self.append(teleport_task)
        return self

    def remove(self, teleport_task: TeleportBetweenPlayers):
        if teleport_task in self.teleport_tasks:
            self.teleport_tasks.remove(teleport_task)

    def __isub__(self, teleport_task: TeleportBetweenPlayers) -> Self:
        self.remove(teleport_task)
        return self

    def run_task(self, source: str, target: str) -> bool:
        try:
            for i in self.teleport_tasks:
                if i.source == source and i.target == target:
                    i.execute()
                    return True
            return False
        except TimeoutError:
            if runtime.server:
                runtime.server.logger.error("outdated_teleport_task")
            return False

    @execute_if(
        lambda: runtime.server is not None and runtime.config is not None, True
    )
    def find_run_task(self, target: str) -> bool:
        assert runtime.server is not None
        assert runtime.config is not None
        tasks_to_run: list[TeleportBetweenPlayers] = []
        current_time: datetime = datetime.now()
        try:
            for i in self.teleport_tasks:
                if i.target == target:
                    if ((current_time - i.create_time).total_seconds() >
                            runtime.config.timeout.teleport):
                        self.remove(i)
                tasks_to_run.append(i)
            if len(tasks_to_run) > 0:
                chosen: TeleportBetweenPlayers = max(
                    tasks_to_run, key=lambda x: x.create_time
                )
                chosen.execute()
                self -= chosen
                return True
            return False
        except TimeoutError:
            return False


class TeleportToAny:
    @execute_if(
        lambda: runtime.server is not None and runtime.config is not None, True
    )
    def __init__(self, source: ExecSource | None = None):
        assert runtime.server is not None
        assert runtime.config is not None
        if not runtime.config.enable_modules.teleport:
            raise FeatureDisabledError('"teleport" is not enabled in config.')
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
