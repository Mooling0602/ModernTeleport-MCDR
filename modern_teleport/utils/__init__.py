# from collections.abc import Callable
from dataclasses import dataclass

# from functools import wraps
# from typing import TypeVar, ParamSpec
from uuid import UUID

from mcdreforged.api.all import (
    CommandContext,
    CommandSource,
)
from auto_uuid_api import is_uuid, local_api
from .execute_if import execute_if

# P = ParamSpec("P")
# T = TypeVar("T")
__all__ = [
    "Player",
    "execute_if",
]


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


# def execute_if(condition: bool | Callable[[], bool], raise_error: bool = False):
#     def decorator(func: Callable[P, T]) -> Callable[P, T | None]:
#         @wraps(func)
#         def wrapper(*args: P.args, **kwargs: P.kwargs) -> T | None:
#             _condition = condition() if callable(condition) else condition
#             if _condition:
#                 return func(*args, **kwargs)
#             else:
#                 if raise_error:
#                     raise RuntimeError("Condition forcely required is not met!")
#                 # 对于MCDR命令处理函数，如果条件不满足且不抛出错误，返回None
#                 # 这样可以避免参数传递错误
#                 if len(args) > 0 and isinstance(args[0], CommandSource):
#                     # 如果是命令处理函数，至少应该有src参数
#                     return None
#             return None

#         return wrapper

#     return decorator
