from mcdreforged.api.all import PluginServerInterface, RTextMCDRTranslation


def tr(
    server: PluginServerInterface, tr_key: str, return_str: bool = False, *args
) -> str | RTextMCDRTranslation:
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
    return str(tr(server, tr_key, True, *args))


def tr_to_rtr(
    server: PluginServerInterface, tr_key: str, *args
) -> RTextMCDRTranslation:
    rtr = tr(server, tr_key, False, *args)
    assert isinstance(rtr, RTextMCDRTranslation)
    return rtr
