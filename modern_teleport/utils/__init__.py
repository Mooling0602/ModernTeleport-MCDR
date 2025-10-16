from typing import Literal, Self
from uuid import UUID

from auto_uuid_api import local_api
from modern_teleport.utils.general_tools import execute_if

from mcdreforged.api.all import (
    CommandContext,
    CommandSource,
    PluginServerInterface,
)

__all__ = ["Player", "execute_if"]
ContextType = Literal["console", "game", "player", "all"]
PlayerDataType = Literal["name", "uuid"]


def tr(
    server: PluginServerInterface,
    tr_key: str,
    return_str: bool = True,
    *args
):
    plgSelf = server.get_self_metadata()
    if tr_key.startswith(f"{plgSelf.id}"):
        translation = server.rtr(f"{tr_key}")
    else:
        if tr_key.startswith("#"):
            translation = server.rtr(tr_key.replace("#", ""), *args)
        else:
            translation = server.rtr(f"{plgSelf.id}.{tr_key}", *args)
    if return_str:
        tr_to_str: str = str(translation)
        return tr_to_str
    else:
        return translation


class FeatureDisabledError(Exception):
    pass


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
        class_match: bool = False
        name_match: bool = False
        uuid_match: bool = False
        if isinstance(value, Player):
            class_match = True
        else:
            return False
        if self.name is not None and value.name is not None:
            name_match = (self.name.lower() == value.name.lower())
        else:
            name_match = (self.name is None) == (value.name is None)
        return (
            class_match is True
            and name_match is True
            and uuid_match is True
        )


if __name__ == "__main__":
    player = Player(uuid="00000000-0000-0000-0000-000000000000")
    player.name = "Steve"
    print(player)
