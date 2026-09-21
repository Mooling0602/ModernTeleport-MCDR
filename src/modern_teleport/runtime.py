"""Plugin runtime for ModernTeleort, provides public variables, global
configurations, and so on."""

from mcdreforged import PluginServerInterface, ServerInterface

from modern_teleport.config import MTPConfig

psi: PluginServerInterface = ServerInterface.psi()
"""MCDR plugin server interface."""

config: MTPConfig = MTPConfig()
"""Plugin global configurations in the whole lifecycle."""


def get_config() -> MTPConfig:
    """Lazy get the config instance."""
    return config
