import asyncio
import modern_teleport.runtime as runtime

from datetime import datetime
from typing import Literal

from mcdreforged.api.all import PluginServerInterface
from location_api import MCPosition, Point3D

_TeleportType = Literal["ask", "invite", "position"]
TeleportRequestOptions = Literal["accept", "reject", "cancel"]


def get_teleport_command(tp_type: _TeleportType, prefix_slash: bool = False):
    prefix: str = ""
    if prefix_slash:
        prefix = "/"
    if tp_type == "ask":
        return "{prefix}tp {{selected_player}} {{target_player}}".format(  # noqa: F524, E501
            prefix=prefix
        )
    elif tp_type == "invite":
        return "{prefix}tp {{target_player}} {{selected_player}}".format(  # noqa: F524, E501
            prefix=prefix
        )
    elif tp_type == "position":
        return "{prefix}tp {{position}}".format(  # noqa: F524, E501
            prefix=prefix
        )
    else:
        raise TypeError("Invalid teleport type")


class TeleportPosition:
    def __init__(
        self,
        server: PluginServerInterface,
        target_player: str | None = None,
        po: MCPosition | Point3D | None = None
    ):
        self.server: PluginServerInterface = server
        self.s = server
        self.target_player: str | None = target_player
        self.po: MCPosition | Point3D | None = None
        self.command: str | None = None

    def set_target(self, target_player: str):
        self.target_player = target_player

    def set_position(self, po: MCPosition | Point3D):
        self.po = po

    def get_command(self) -> str:
        if not self.target_player:
            raise TypeError(
                "No valid player name given. Please `set_target` first."
            )
        if not self.po:
            raise TypeError(
                "No valid position given. Please `set_position` first."
            )
        if isinstance(self.po, MCPosition):
            return (
                f"execute in {self.po.dimension} run tp "
                f"{self.target_player} {self.po.point.x} "
                f"{self.po.point.y} {self.po.point.z}"
            )
        elif isinstance(self.po, Point3D):
            return (
                f"tp {self.target_player} {self.po.x} {self.po.y} {self.po.z}"
            )
        else:
            raise TypeError("No valid position given.")

    def execute(self, debug: bool = False, src_player: str | None = None):
        command: str = self.get_command()
        if "execute" not in command:
            self.s.logger.warning(
                "No dimension given, will teleport the player only "
                "in the current dimension."
            )
        if debug:
            self.s.logger.info(f"> {command}")
            if src_player:
                self.s.tell(src_player, f"> {command}")
        else:
            self.s.execute(command)


class TeleportRequest:
    def __init__(
        self,
        server: PluginServerInterface,
        tp_type: _TeleportType,
        selected_player: str,
        target_player: str,
    ):
        if tp_type == "position":
            raise TypeError(
                "Teleporting to a position is not supported here, "
                "use TeleportPosition instead."
            )
        self.server: PluginServerInterface = server
        self.s = self.server  # alias
        self.tp_type: _TeleportType = tp_type
        self.tp_task: asyncio.Task | None = None
        self.wait_confirm: asyncio.Future = asyncio.Future()
        self._command_format: str = get_teleport_command(tp_type)
        self.selected_player: str = selected_player
        self.target_player: str = target_player
        self.command: str = self._command_format.format(
            selected_player=self.selected_player,
            target_player=self.target_player,
        )
        self.start_time: datetime | None = None

    async def set_task(self):
        assert runtime.config is not None
        self.start_time = datetime.now()
        timeout: float = runtime.config.timeout.teleport
        self.tp_task = asyncio.create_task(
            asyncio.wait_for(fut=self.wait_confirm, timeout=timeout)
        )

        self.s.tell(self.target_player, "tpr.receive")

    def accept(self):
        if not self.wait_confirm.done():
            self.wait_confirm.set_result(True)
            self.s.tell(self.target_player, "tpr.accept")
            self.s.tell(self.selected_player, "tpr.accepted")

    def reject(self):
        if not self.wait_confirm.done():
            self.wait_confirm.set_result(False)
            self.s.tell(self.target_player, "tpr.reject")
            self.s.tell(self.selected_player, "tpr.rejected")

    def cancel(self, reason: str | None = None):
        if not self.wait_confirm.done():
            self.wait_confirm.cancel()
            if self.s.is_server_running():
                self.s.tell(self.target_player, "tpr.cancel")
                self.s.tell(self.selected_player, "tpr.cancelled")

    async def wait_for_target_player(self) -> bool:
        try:
            result: bool = await self.wait_confirm
            if result:
                self.s.logger.info("tpr.accept")
                self.s.execute(self.command)
                return True
            else:
                self.s.logger.info("tpr.failed")
                return False
        except asyncio.TimeoutError:
            self.when_timeout()
            return False
        except asyncio.CancelledError:
            self.when_cancelled()
            return False

    def when_timeout(self):
        self.s.logger.error("tpr.timeout")
        self.s.tell(self.selected_player, "tpr.timeout")
        self.s.tell(self.target_player, "tpr.timeout")

    def when_cancelled(self):
        if self.tp_type == "ask":
            self.s.logger.error(
                f"tpr.cancelled_by_unload: {self.selected_player}"
                f" -> {self.target_player}"
            )
        else:
            self.s.logger.error(
                f"tpr.cancelled_by_unload: {self.target_player}"
                f" -> {self.selected_player}"
            )


class AsyncSessionManager:
    def __init__(self, server: PluginServerInterface):
        self.server: PluginServerInterface = server
        self.s = self.server  # alias
        self.tp_tasks: list[TeleportRequest] = []

    async def add(self, tp_task: TeleportRequest):
        if len(self.tp_tasks) > 0:
            for i in self.tp_tasks:
                if (
                    i.selected_player.lower()
                    == tp_task.selected_player.lower()
                    and i.target_player.lower()
                    == tp_task.target_player.lower()
                ) or (
                    i.selected_player.lower() == tp_task.target_player.lower()
                    and i.target_player.lower()
                    == tp_task.selected_player.lower()
                ):
                    self.s.tell(tp_task.selected_player, "tpr.exists")
                    self.s.logger.warning("tpr.exists")
                    return
        self.tp_tasks.append(tp_task)
        try:
            await tp_task.set_task()
            await tp_task.wait_for_target_player()
        finally:
            if tp_task in self.tp_tasks:
                self.tp_tasks.remove(tp_task)

    def schedule_add(self, tp_task: TeleportRequest):
        async def add_task():
            await self.add(tp_task)

        self.s.schedule_task(add_task())

    def confirm_latest_request(
        self, target_player: str, option: TeleportRequestOptions
    ):
        tasks_to_do: list[TeleportRequest] = []
        for i in self.tp_tasks:
            if i.target_player.lower() == target_player.lower():
                tasks_to_do.append(i)

        if not tasks_to_do:
            return

        latest_task: TeleportRequest = max(
            tasks_to_do,
            key=lambda task: task.start_time
            if task.start_time
            else datetime.min,
        )
        if option == "accept":
            latest_task.accept()
        elif option == "reject":
            latest_task.reject()
        elif option == "cancel":
            latest_task.cancel()
        else:
            raise ValueError(f"Invalid option: {option}")

    def cancel_all_requests(self):
        for i in self.tp_tasks:
            i.cancel()
