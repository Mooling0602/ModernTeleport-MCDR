from mcdreforged import AsyncRconConnection, PluginServerInterface

from modern_teleport.utils import execute_if

RconConnector: AsyncRconConnection | None = None


async def connect_rcon(server: PluginServerInterface):
    global RconConnector
    RconConnector = AsyncRconConnection(
        server.get_mcdr_config()["rcon.address"],
        server.get_mcdr_config()["rcon.port"],
        server.get_mcdr_config()["rcon.password"],
    )
    success = await RconConnector.connect()
    if not success:
        RconConnector = None


@execute_if(
    lambda: RconConnector is not None,
    True,
    "Async rcon connection is not established.",
)
async def rcon_query(command: str) -> str | None:
    assert isinstance(RconConnector, AsyncRconConnection)
    return await RconConnector.send_command(command)
