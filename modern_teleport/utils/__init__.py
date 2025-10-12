from dataclasses import dataclass
from typing import Literal, Self
from uuid import UUID

from auto_uuid_api import local_api
from modern_teleport.utils.execute_if import execute_if

from mcdreforged.api.all import (
    CommandContext,
    CommandSource,
)

__all__ = ["Player", "execute_if", "ExecSourceType"]

ExecSourceType = Literal["console", "player", "remote"]
PlayerDataType = Literal["name", "uuid"]


class FeatureDisabledError(Exception):
    pass


@dataclass
class ExecSource:
    source_type: ExecSourceType
    source_name: str | None = None


# @dataclass
# class Player:
#     name: str
#     uuid: UUID

#     def __init__(self, name: str, uuid: str | UUID) -> None:
#         if isinstance(uuid, str):
#             self.uuid: UUID = UUID(uuid)
#         else:
#             self.uuid: UUID = uuid
#         self.name: str = name

#     @classmethod
#     def on_debug(cls, src: CommandSource, ctx: CommandContext):
#         player: str | None = ctx.get("player", None)
#         if player and not is_uuid(player):
#             if local_api:
#                 uuid: str | None = local_api.get(player)
#                 if uuid:
#                     src.reply(str(cls(player, uuid)))


class Player:
    def __init__(
        self, name: str | None = None, uuid: str | UUID | None = None
    ) -> None:
        self.name: str | None = name
        self.uuid: UUID | None = None
        if isinstance(uuid, str):
            self.uuid: UUID | None = UUID(uuid)
        if not name and not uuid:
            raise TypeError("No information provided for this player.")
        self.try_complete_profile()

    def try_complete_profile(self):
        if not self.name and self.uuid:
            if local_api:
                _result = local_api.get(str(self.uuid))
                self.name = _result
        if not self.uuid and self.name:
            if local_api:
                _result: str | None = local_api.get(self.name)
                self.uuid = UUID(_result)

    def get_string(self, data_type: PlayerDataType, auto: bool = False) -> str:
        if data_type == "name":
            if self.name:
                return self.name
            elif auto and self.uuid:
                return str(self.uuid)
            else:
                raise TypeError("Unable to get name for the player.")
        elif data_type == "uuid":
            if self.uuid:
                return str(self.uuid)
            elif auto and self.name:
                return self.name
            else:
                raise TypeError("Unable to get uuid for the player.")
        else:
            raise ValueError("Invalid data type.")

    @classmethod
    def on_debug_command(cls, src: CommandSource, ctx: CommandContext):
        _player: str | None = ctx.get("player", None)
        if _player:
            player: Self = cls(_player)
            src.reply(str(player))

    def __str__(self) -> str:
        return f"Player(name={self.name}, uuid={self.uuid})"

    def __eq__(self, value: object) -> bool:
        return (
            isinstance(value, Player)
            and self.name == value.name
            and self.uuid == value.uuid
        )


if __name__ == "__main__":
    player = Player(uuid="00000000-0000-0000-0000-000000000000")
    player.name = "Steve"
    print(player)
