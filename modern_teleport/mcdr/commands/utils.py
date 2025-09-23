from mcdreforged.api.all import SimpleCommandBuilder
from mcdreforged.command.builder.nodes.basic import RUNS_CALLBACK


def build_exec_with_multiple_commands(
    builder: SimpleCommandBuilder, command_list: list[str], func: RUNS_CALLBACK
):
    for i in command_list:
        builder.command(i, func)
