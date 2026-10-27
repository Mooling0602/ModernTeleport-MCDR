from enum import StrEnum, auto


class MTPModules(StrEnum):
    """Enum class for MTP modules."""

    BACK = auto()
    COST = auto()
    HOME = auto()
    TPMANAGER = "tpm"
    WARP = auto()
    WAYPOINT = auto()
