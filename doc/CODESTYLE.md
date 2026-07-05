# Code Style

The purpose of this document is to constrain the text style and coding standards of the code, ensuring readability and maintainability.

## Docstrings

Docstrings are strings in Python used to describe functions, classes, modules, etc. They should contain information such as the name, parameters, return values, and exceptions of functions or classes.

In the source code of this project, docstrings use the reStructuredText style and generate well-readable documentation through Sphinx.

## I18n

MCDR plugins typically use the `PluginServerInterface.tr()` method to obtain specified translation results, which requires passing a translation key string as a parameter. To improve development efficiency, translation key strings are usually used directly in the early development stage, and later switched to using the `tr()` method to obtain translation results as needed.
