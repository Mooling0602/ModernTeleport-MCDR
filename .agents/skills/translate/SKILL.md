---
name: translate
description: Use when do translation tasks for source codes in this project.
---

## Instructions

MCDReforged provides `tr()` and `rtr()` method through `PluginServerInterface` API, it gets translation result for further logging or display to the console or the player. By passing a translation key string as an argument to `tr()` or `rtr()` method, MCDR can find the correct translated content result in directory `lang/` in the plugin pack.

For convenience, a wrapper method `tr()` (different from `PluginServerInterface.tr()`) is typically defined in the `utils.py` module.

> In this project, the module is located in `src/modern_teleport`.

What you need to do is to modify every string arguments matches the description in "I18n" part of [Code Style](doc/CODESTYLE.md) or similar to a translation key, and rewrite them with method `tr()` from the `utils.py` module. You should read the function first when doing translation tasks.

The translation files are located in `src/lang` in this project, and they are named with language codes. Modify them as the need.
