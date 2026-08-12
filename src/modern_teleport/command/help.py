from mcdreforged.api.all import CommandSource, RText, RTextList

## > !!mtp | > !!mtp help
## Rich functional modern design for Minecraft teleportation.
## Usage: !!mtp
MTP_MAIN_HELP_PAGE = RTextList(
    RText("tr#plugin_desc"),
)


def show_mtp_main_help(src: CommandSource):
    src.reply("Not implemented yet.")
