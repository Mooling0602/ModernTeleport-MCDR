"""Useful tools and interfaces this plugin uses."""

from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import ParamSpec, TypeVar

from mcdreforged import PluginServerInterface

P = ParamSpec("P")
R = TypeVar("R")


def execute_if(
    condition: bool | Callable[[], bool],
    raise_error: bool = False,
    error_message: str = "Required condition is not met.",
) -> Callable[[Callable[P, R]], Callable[P, R | None]]:
    """A decorator to preset conditions before execute a function.

    :param condition: The required condition need to check.
    :param raise_error: Whether to raise an error if the condition is
        not met.
    :param error_message: The error message to raise, will be ignored if
        raise_error is False.
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R | None]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R | None:
            actual_condition = (
                condition() if callable(condition) else condition
            )
            if actual_condition:
                return func(*args, **kwargs)
            else:
                if raise_error:
                    raise RuntimeError(error_message)
                return None

        return wrapper

    return decorator


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
