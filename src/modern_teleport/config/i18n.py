"""Internationalization utilities for the ModernTeleport plugin."""

from mcdreforged.api.all import PluginServerInterface, RTextMCDRTranslation


def tr(
    server: PluginServerInterface, tr_key: str, return_str: bool = False, *args
) -> str | RTextMCDRTranslation:
    """Translate a key to a string or RTextMCDRTranslation(also called
    "rtr") object.

    :param server: The plugin server interface.
    :param tr_key: The translation key.
    :param return_str: Whether to return a string or an
        RTextMCDRTranslation object. Default is False, which returns an
        RTextMCDRTranslation object.
    :param args: The arguments to format the translation string.
    :return: The translated string or RTextMCDRTranslation object.
    """
    plg_id = server.get_self_metadata().id
    if tr_key.startswith(f"{plg_id}"):
        translation = server.rtr(f"{tr_key}")
    else:
        if tr_key.startswith("#"):
            translation = server.rtr(tr_key.replace("#", ""), *args)
        else:
            translation = server.rtr(f"{plg_id}.{tr_key}", *args)
    if return_str:
        tr_to_str: str = str(translation)
        return tr_to_str
    else:
        return translation


def tr_to_str(server: PluginServerInterface, tr_key: str, *args) -> str:
    """Translate a key to a string.

    Quick wrapper for `tr()` with `return_str=True`.
    """
    return str(tr(server, tr_key, True, *args))


def tr_to_rtr(
    server: PluginServerInterface, tr_key: str, *args
) -> RTextMCDRTranslation:
    """Translate a key to an RTextMCDRTranslation object.

    Quick wrapper for `tr()` with `return_str=False`.
    """
    rtr = tr(server, tr_key, False, *args)
    assert isinstance(rtr, RTextMCDRTranslation)
    return rtr
