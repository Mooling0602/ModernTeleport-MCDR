from mcdreforged.api.all import (
    CommandContext,
    CommandSource,
    RText
)


def get_help_page_title(text_title: str) -> RText:
    """Get mojang style command title.

    Args:
        text_title (str): The title texts.

    Returns:
        RText: MCDReforged RText compenent, Python implemention of Minecraft \
            text compenent.
    """
    return RText("")


def on_command_help(src: CommandSource, ctx: CommandContext):
    """Main command help page.

    Args:
        src (CommandSource): Provided by MCDReforged.
        ctx (CommandContext): Provided by MCDReforged.

    Contents:
        pass
    """
    src.reply("not_implemented_yet")
