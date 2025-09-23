import modern_teleport.runtime as runtime

from concurrent.futures import ThreadPoolExecutor, Future
from typing import Literal

from modern_teleport.utils import execute_if

rcon_module = Literal["mcdr", "async_rcon"]


class RconManager:
    def __init__(self, module: rcon_module = "mcdr") -> None:
        self.module: rcon_module = module

    @execute_if(lambda: runtime.server is not None)
    def get_from_mcdr(self, command: str) -> str | None:
        assert runtime.server is not None
        if not runtime.server.is_rcon_running():
            raise RuntimeError("rcon.mcdr.not_running")
        with ThreadPoolExecutor(max_workers=1) as executor:
            future: Future[str | None] = executor.submit(
                runtime.server.rcon_query, command
            )
        try:
            result: str | None = future.result(timeout=0.5)
        except TimeoutError:
            runtime.server.logger.warning("rcon.timeout")
            try:
                runtime.server._mcdr_server.connect_rcon()
                result: str | None = future.result(timeout=5)
            except TimeoutError:
                raise TimeoutError("rcon.no_response")
        return result

    def get_from_async_rcon(self, _: str) -> str | None:
        raise NotImplementedError("module.not_implemented_yet")

    @execute_if(lambda: runtime.server is not None)
    def get(self, command: str) -> str | None:
        if self.module == "mcdr":
            return self.get_from_mcdr(command)
        elif self.module == "async_rcon":
            if runtime.server:
                runtime.server.logger.warning("module.not_implemented_yet")
            # return self.get_from_async_rcon(command)
            return self.get_from_mcdr(command)
