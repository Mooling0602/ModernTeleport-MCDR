import modern_teleport.runtime as runtime

from typing import Literal


class RconManager:
    def __init__(self, module: Literal["mcdr", "async_rcon"] = "mcdr") -> None:
        self.server = runtime.server
        self.module = module
