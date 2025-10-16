import os
import modern_teleport.runtime as runtime

from enum import StrEnum, auto
from mcdreforged.api.all import PluginServerInterface
from auto_uuid_api import is_uuid, local_api
from modern_teleport.utils import execute_if


class MTP(StrEnum):
    BACK = auto()
    HOME = auto()
    WARP = auto()
    TPRequest = "tpr"


class DataManager:
    @execute_if(lambda: runtime.config is not None, True)
    def __init__(self, server: PluginServerInterface) -> None:
        assert runtime.config is not None
        self.config: runtime.MainConfig = runtime.config
        self.server: PluginServerInterface = server
        self.s = self.server
        self.data_folder: str = os.path.join(
            self.s.get_data_folder(),
            "data"
        )
        self.world_dir: str | None = None
        self.server_dir: str | None = self.s.get_mcdr_config().get(
            "working_directory", None
        )
        if self.server_dir:
            self.world_dir = os.path.join(
                self.server_dir, runtime.config.data_storage.world_name
            )
        if self.world_dir and os.path.exists(self.world_dir):
            self.data_folder = os.path.join(
                self.world_dir,
                self.s.get_self_metadata().id,
            )

    def get_player_folder(self, name_or_uuid: str) -> str:
        assert runtime.config is not None
        if is_uuid(name_or_uuid):
            return os.path.join(self.data_folder, name_or_uuid)
        else:
            if runtime.config.identity_mode == "name":
                return os.path.join(self.data_folder, name_or_uuid)
            _uuid: str | None = local_api.get_uuid(name_or_uuid)
            if _uuid:
                return os.path.join(self.data_folder, _uuid)
            else:
                raise RuntimeError("error.no_uuid")

    def get_data_file_path(
        self, module: MTP, name_or_uuid: str | None = None
    ) -> str | None:
        if module == MTP.WARP or module == MTP.TPRequest:
            return os.path.join(self.data_folder, f"{module}.json")
        else:
            if not name_or_uuid:
                self.server.logger.error("data.need_name_or_uuid")
                raise TypeError("data.need_name_or_uuid")
            return os.path.join(
                self.data_folder,
                self.get_player_folder(name_or_uuid),
                f"{module}.json"
            )


if __name__ == "__main__":
    print("Print all MTP(ModernTeleport) modules for testing enum.")
    mtp_modules: list[str] = [MTP.BACK, MTP.HOME, MTP.WARP, MTP.TPRequest]
    for i in mtp_modules:
        print(i, isinstance(i, str))
