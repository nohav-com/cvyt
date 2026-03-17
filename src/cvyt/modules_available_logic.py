# -*- coding: utf-8 -*-
"""Available modules for the main widget. Using AbstractListModel."""

import logging

from PySide6 import QtCore

from cvyt.common_update import CommonUpdate

__all__ = ['ModelAvailableModules']

logger = logging.getLogger(__name__)


class ModelAvailableModules(QtCore.QAbstractListModel):
    """Simple logic connected to the main menu placed on the left side,
    providing an overview list of available modules that can be used.

    Uses PySide6 AbstractListModel to experiment with it and see its
    pros and cons.

    Args:
    config = config object
    """
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.config = kwargs.get('config', None)
        self.common_update = CommonUpdate(*args, **kwargs)

    def rowCount(self, _):
        return self.common_update.get_count_of_available_modules()

    def data(self, index, role=QtCore.Qt.DisplayRole) -> str:
        """Get the data/name for the specified row/line in the list.

        Args:
        index = row from list to be processed
        role = role flag(how to process output)

        Returns:
        name of the module
        """
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            return self.get_name_of_module(row)

    def get_name_of_module(self, position) -> str | None:
        """Get the name of the module.

        Args:
        position = row index from the list

        Returns:
        name of the module(file name)
        """
        module_name = None
        for index, (name, _) in enumerate(
                self.common_update.get_available_modules()):
            if index == position:
                module_name = name
                break
        return module_name

    def get_value_for_key_in_module(self, module: str, key: str):
        """Get the value for a key from the info object of a specific module.

        Args:
        module (str)= module name
        key (str)= key to search for

        Returns:
        The value for the key
        """
        return self.common_update.get_value_for_key(module, key)

    def create_modules_list(self):
        """Create a list of all available modules.

        This means finding the folders, scanning them, validating them,
        collecting info and storing the info in the expected format.
        """
        modules_root = self.config.get_value_for_key(
            self.common_update.get_modules_root_keys_chain())
        self.common_update.create_update_list(
            modules_root
        )

    def get_init_file(self, module_info: dict) -> str | None:
        """Get the init file(path to it) for specified module.

        Args:
        module_name (dict)= name of the module

        Returns:
        path to the init file
        """
        init_file = None
        if "__init__.py" in module_info:
            init_file = module_info.get("__init__.py", None)
        return init_file

    def get_module_info(self, module_name: str):
        """Get info about the module.

        Args:
        module_name (str)= name of the module
        """
        return self.common_update.get_detailed_info_about_module(module_name)
