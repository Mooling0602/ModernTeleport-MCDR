import modern_teleport.runtime as runtime

from enum import StrEnum, auto


class MTP(StrEnum):
    BACK = auto()
    HOME = auto()
    WARP = auto()


class DataManager:
    pass


if __name__ == "__main__":
    print("Print all MTP modules for testing enum.")
    mtp_modules: list[str] = [
        MTP.BACK,
        MTP.HOME,
        MTP.WARP
    ]
    for i in mtp_modules:
        print(i)
