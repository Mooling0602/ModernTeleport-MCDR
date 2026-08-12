from pathlib import Path

from mcdreforged.api.all import PluginServerInterface


def extract_file(
    server: PluginServerInterface,
    file_path: Path | str,
    target_path: Path | str,
):
    with (
        server.open_bundled_file(str(file_path)) as fh,
        open(target_path, "wb") as f,
    ):
        f.write(fh.read())
