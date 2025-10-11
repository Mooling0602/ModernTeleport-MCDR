import asyncio
import modern_teleport.runtime as runtime

from typing import Literal, TYPE_CHECKING
from beartype import beartype

from modern_teleport.utils import Player

if TYPE_CHECKING:
    from mcdreforged.api.all import (
        PluginServerInterface,
    )

_TeleportType = Literal["ask", "invite", "position"]


@beartype
def get_teleport_command(tp_type: _TeleportType, prefix_slash: bool = False):
    prefix: str = ""
    if prefix_slash:
        prefix = "/"
    if tp_type == "ask":
        return "{prefix}tp {selected_player} {target_player}".format(  # noqa: F524, E501
            prefix=prefix
        )
    elif tp_type == "invite":
        return "{prefix}tp {target_player} {selected_player}".format(  # noqa: F524, E501
            prefix=prefix
        )
    else:
        return "{prefix}tp {position}".format(  # noqa: F524, E501
            prefix=prefix
        )


class TeleportRequest:
    def __init__(
        self,
        server: PluginServerInterface,
        tp_type: _TeleportType,
        selected_player: Player | str,
        target_player: Player | str,
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
        _selected_player: str = ""
        _target_player: str = ""
        if isinstance(selected_player, Player):
            _selected_player = str(selected_player.uuid)
        if isinstance(target_player, Player):
            _target_player = str(target_player.uuid)
        if isinstance(selected_player, str):
            _selected_player = selected_player
        if isinstance(target_player, str):
            _target_player = target_player
        self.selected_player: str = _selected_player
        self.target_player: str = _target_player
        self.command: str = self._command_format.format(
            selected_player=self.selected_player,
            target_player=self.target_player,
        )

    async def set_task(self):
        assert runtime.config is not None
        timeout: float = runtime.config.timeout.teleport
        self.tp_task = asyncio.create_task(
            asyncio.wait_for(fut=self.wait_confirm, timeout=timeout)
        )

        def handle_timeout(task: asyncio.Task):
            exception: BaseException | None = task.exception()
            if exception is not None:
                if isinstance(exception, asyncio.TimeoutError):
                    self.when_timeout()
                elif isinstance(exception, asyncio.CancelledError):
                    pass
                else:
                    raise exception

        self.tp_task.add_done_callback(handle_timeout)

    def accept(self):
        if not self.wait_confirm.done():
            self.wait_confirm.set_result(True)

    def reject(self):
        if not self.wait_confirm.done():
            self.wait_confirm.set_result(False)

    def cancel(self):
        if not self.wait_confirm.done():
            self.wait_confirm.cancel()

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

    def when_timeout(self):
        self.s.logger.error("tpr.timeout")


class AsyncSessionManager:
    def __init__(self, server: PluginServerInterface):
        self.server: PluginServerInterface = server
        self.s = self.server  # alias
        self.tp_tasks: list[TeleportRequest] = []
