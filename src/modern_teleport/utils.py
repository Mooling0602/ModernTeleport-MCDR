"""Useful tools and interfaces this plugin uses."""

from pathlib import Path

from mcdreforged import PluginServerInterface


def extract_file(
    server: PluginServerInterface,
    file_path: Path | str,
    target_path: Path | str,
):
    """Extract a file from the plugin bundle (packaged *.mcdr file) to a
    target path.

    Also as a wrapper for `psi.open_bundled_file()`.
    :param server: MCDR plugin server interface.
    :param file_path: The resource file's path in the plugin bundle.
    :param target_path: The target path to extract the resource file to.
    """
    with (
        server.open_bundled_file(str(file_path)) as fh,
        open(target_path, "wb") as f,
    ):
        f.write(fh.read())
