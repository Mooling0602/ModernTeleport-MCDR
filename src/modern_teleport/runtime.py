from mcdreforged import PluginServerInterface, ServerInterface

from modern_teleport.config import MTPConfig

psi: PluginServerInterface = ServerInterface.psi()
config: MTPConfig = MTPConfig()
