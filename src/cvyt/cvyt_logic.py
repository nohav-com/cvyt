# -*- coding: utf-8 -*-
"""Main window/widget logic."""

import importlib.util
import logging
import re
import shutil
import sys
from pathlib import Path
from cvyt.config_logic import ConfigLogic

__all__ = ['CvytLogic']


logger = logging.getLogger(__name__)


class CvytLogic():
    """Logic for Cvyt UI."""
    def clean_sys_modules(self, key: str):
        """Remove all evidence of presence of module for key.add()

        Need to remove module with given name, so it can be imported again.

        Args:
        key = name of the module
        """
        keys_to_remove = []
        for item in sys.modules:
            if item.startswith(key):
                keys_to_remove.append(item)
        for key in keys_to_remove:
            del sys.modules[key]
            logger.info(
                "Removing imported module '%s' from sys.module.", key)

    def import_module(
            self,
            module_name: str,
            module_info: dict,
            app,
            config: ConfigLogic):
        """Import module.

        Try to all possible options how to import the module

        Args:
        module_name = name of the module
        module_info = infor about module
        app = main window(widget) - passed as param
        config = app config object - passed as param
        """
        module_loaded = None
        module_class_name = None
        main_file = None
        module = None
        module_instance = None
        module_init = None

        # Get parent folder of source code
        parent = None
        if module_info:
            for item in module_info:
                if item.endswith(".py"):
                    parent = Path(module_info.get(item)).parent
        else:
            logger.error(
                "Cannot processed, no module info available")
            return
        # Get rid off trash
        if parent:
            logger.info("Parent folder is '%s'.", str(parent))
            to_remove = parent.joinpath('__pycache__')
            if to_remove.exists():
                logger.info("Cleaning trash('__pycache__').")
                shutil.rmtree(str(to_remove), ignore_errors=True)
        # Remove previous import
        self.clean_sys_modules(module_name)

        # Find the right file - widget
        for item in module_info:
            if item.endswith("widget.py"):
                main_file = module_info.get(item)
            # Get module __init__ file if exists
            if item == "__init__.py":
                module_init = module_info.get(item)

        # Check if main file exist
        if not Path(main_file).exists():
            # Main file doesnt exist
            logger.warning(
                "Can not find main file for module '%s'", module_name)

        # Get main class name from module_config.json
        module_class_name = module_info and module_info.get("class_name", None)
        if main_file and module_class_name:
            module = self.load_module_from_file(
                    module_name,
                    module_class_name,
                    main_file)

        # Lets try init file(searching for import of main class)
        if not module and module_init:
            try:
                module_loaded = importlib.import_module(
                    module_name, module_init)
                if module_loaded:
                    for item in dir(module_loaded):
                        # Skip the trash
                        if not re.search("__(.*)__", item):
                            module = getattr(module_loaded, item)
                        if type(module).__name__.lower() == "objecttype":
                            break
            except Exception as e:
                logger.info(
                    "Cannot import module via '__init__' file(%s).", e)
                module = None
        else:
            logger.info(
                "Cannot import module via init file, file doesnt exist.")

        if not module and main_file:
            module_class_name = self.get_claass_name_from_all(main_file)
            if module_class_name:
                module = self.load_module_from_file(
                    module_name,
                    module_class_name,
                    main_file)

        # Init the module and return instance
        if module and app and config:
            try:
                module_instance = module(
                    app=app,
                    confing=config
                )
            except Exception as e:
                logger.error("Cannot import module and add the tab(%e).", e)

        return module_instance

    def get_claass_name_from_all(self, main_file: str) -> str:
        """Get class name form '__all__' variable.

        Args:
        main_file = file where to look

        Returns:
        Name or None
        """
        class_name = None
        if main_file and Path(main_file).exists():
            with open(main_file, "r", encoding='utf-8') as file_in:
                lines = file_in.readlines()
                for line in lines:
                    groups = re.match(
                        r"(?P<all_tag>__all__)\ =\ \[\'(?P<class_tag>\w+)\'",
                        line.strip())
                    if groups:
                        class_name = groups.group('class_tag')
                        break
        return class_name

    def load_module_from_file(
            self, module_name: str, module_class_name: str, module_path: str):
        """Load module from file.

        Args:
        module_name = name of module(file)
        module_class_name = name of module's main class
        module_path = path to file with main class

        Returns:
        Module to be instantiated, or None
        """
        module = None
        if module_name and module_class_name and module_path:
            try:
                spec = importlib.util.spec_from_file_location(
                        module_class_name,
                        module_path
                    )
                module_loaded = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module_loaded
                spec.loader.exec_module(module_loaded)
                module = getattr(module_loaded, module_class_name)
            except Exception as e:
                logger.error(
                    "Can not import module '%s' because: %s.",
                    module_name,
                    e)
                module = None
        else:
            logger.info("Module file name is '%s'.", module_name)
            logger.info("Module class name is '%s'", module_class_name)
            logger.info("Module file is at '%s'", module_path)
            logger.error(
                "Cannot import module. Missing arguments.")
        return module
