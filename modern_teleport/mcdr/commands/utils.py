from mcdreforged.api.all import (
    SimpleCommandBuilder,
    CommandSource,
    CommandContext,
)
from mcdreforged.command.builder.nodes.basic import RUNS_CALLBACK


def build_exec_with_multiple_commands(
    builder: SimpleCommandBuilder, command_list: list[str], func: RUNS_CALLBACK
):
    for i in command_list:
        builder.command(i, func)


def auto_get_player_from_src(
    src: CommandSource,
    ctx: CommandContext,
    argument: str | None = None
) -> str | None:
    player: str | None = ctx.get("player", None)
    if argument:
        player = ctx.get(argument, None)
    if src.is_console:
        if not player:
            src.reply("command.missing_argument.player")
            return None
        return player
    elif src.is_player:
        if player:
            src.reply("command.argument_too_many")
            return None
        return src.player  # pyright: ignore[reportAttributeAccessIssue]
