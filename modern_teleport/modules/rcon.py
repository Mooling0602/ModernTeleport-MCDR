import re
import modern_teleport.runtime as runtime

from concurrent.futures import ThreadPoolExecutor, Future
from typing import Literal
from location_api import Point3D, MCPosition
from modern_teleport.utils import execute_if

rcon_module = Literal["mcdr", "async_rcon"]


class RconManager:
    def __init__(self, module: rcon_module = "mcdr") -> None:
        self.module: rcon_module = module

    @execute_if(lambda: runtime.server is not None and runtime.config is not None)
    def get_from_mcdr(self, command: str) -> str | None:
        assert runtime.server is not None
        assert runtime.config is not None
        if not runtime.server.is_rcon_running():
            raise RuntimeError("rcon.mcdr.not_running")
        with ThreadPoolExecutor(max_workers=1) as executor:
            future: Future[str | None] = executor.submit(
                runtime.server.rcon_query, command
            )
        try:
            result: str | None = future.result(timeout=runtime.config.timeout.rcon_wait)
        except TimeoutError:
            runtime.server.logger.warning("rcon.timeout")
            try:
                runtime.server._mcdr_server.connect_rcon()
                result: str | None = future.result(
                    timeout=runtime.config.timeout.rcon_failed
                )
            except TimeoutError:
                raise TimeoutError("rcon.no_response")
        return result

    def get_from_async_rcon(self, _: str) -> str | None:
        raise NotImplementedError("module.not_implemented_yet")

    @execute_if(lambda: runtime.server is not None)
    def get(self, command: str) -> str | None:
        result: str | None = None
        if self.module == "mcdr":
            result = self.get_from_mcdr(command)
        elif self.module == "async_rcon":
            if runtime.server:
                runtime.server.logger.warning("module.not_implemented_yet")
            # return self.get_from_async_rcon(command)
            result = self.get_from_mcdr(command)
        if runtime.server:
            runtime.server.logger.info(result)
        return result

    def get_online_players(self) -> list[str] | None:
        reply: str | None = self.get("list")
        if reply:
            match: re.Match[str] | None = re.match(
                r"There are \d+ of a max of \d+ players online:", reply
            )
            if match:
                names_section: str = reply[match.end() :].strip()
                if names_section:
                    online_list: list[str] = [
                        name.strip()
                        for name in names_section.split(",")
                        if name.strip()
                    ]
                else:
                    online_list = []
                return online_list

    def get_player_pos(self, player: str) -> MCPosition | None:
        pos_info: str | None = self.get(f"data get entity {player} Pos")
        dim_info: str | None = self.get(f"data get entity {player} Dimension")
        if pos_info and dim_info:
            if pos_info != "No entity was found" and dim_info != "No entity was found":
                pos: list[str] = pos_info.split(":")[1].strip().strip("[]").split(", ")
                position: list = [float(coord[:-1]) for coord in pos]
                dimension = dim_info.split(": ", 1)[1].strip().strip('"')
                return MCPosition(
                    Point3D(*position),
                    dimension,
                )
