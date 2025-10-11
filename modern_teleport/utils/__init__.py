from dataclasses import dataclass
from typing import Literal, TYPE_CHECKING
from uuid import UUID

from auto_uuid_api import is_uuid, local_api
from .execute_if import execute_if

if TYPE_CHECKING:
    from mcdreforged.api.all import (
        CommandContext,
        CommandSource,
    )

__all__ = ["Player", "execute_if", "ExecSourceType"]

ExecSourceType = Literal["console", "player", "remote"]


class FeatureDisabledError(Exception):
    pass


@dataclass
class ExecSource:
    source_type: ExecSourceType
    source_name: str | None = None


@dataclass
class Player:
    name: str
    uuid: UUID

    def __init__(self, name: str, uuid: str | UUID) -> None:
        if isinstance(uuid, str):
            self.uuid: UUID = UUID(uuid)
        else:
            self.uuid: UUID = uuid
        self.name: str = name

    @classmethod
    def on_debug(cls, src: CommandSource, ctx: CommandContext):
        player: str | None = ctx.get("player", None)
        if player and not is_uuid(player):
            if local_api:
                uuid: str | None = local_api.get(player)
                if uuid:
                    src.reply(str(cls(player, uuid)))
