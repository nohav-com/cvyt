# -*- coding: utf-8 -*-
"""Logic for the main window/widget."""

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
    """Logic for the Cvyt UI."""
    def clean_sys_modules(self, key: str):
        """Remove all traces of a module for key.

        This removes the module with the given name so it can be imported
        again.

        Args:
        key (str)= the name of the module
        """
        keys_to_remove = []
        for item in sys.modules:
            if item.startswith(key):
                keys_to_remove.append(item)
        for key in keys_to_remove:
            del sys.modules[key]
            logger.info(
                "Removing the imported module '%s' from sys.module.", key)

    def import_module(
            self,
            module_name: str,
            module_info: dict,
            app,
            config: ConfigLogic):
        """Import a module.

        Attempt all possible ways to import the module.

        Args:
        module_name (str)= name of the module
        module_info (dict)= info about the module
        app = main window(widget) - passed as a param
        config (ConfigLogic)= app config object - passed as a param
        """
        module_loaded = None
        module_class_name = None
        main_file = None
        module = None
        module_instance = None
        module_init = None

        # Get the parent folder of the source code
        parent = None
        if module_info:
            for item in module_info:
                if item.endswith(".py"):
                    parent = Path(module_info.get(item)).parent
        else:
            logger.error(
                "Cannot processed, no module info available.")
            return
        # Get rid of the trash
        if parent:
            logger.info("Parent folder is '%s'.", str(parent))
            to_remove = parent.joinpath('__pycache__')
            if to_remove.exists():
                logger.info("Cleaning trash('__pycache__').")
                shutil.rmtree(str(to_remove), ignore_errors=True)
        # Remove previous import
        self.clean_sys_modules(module_name)

        # Find the correct file - widget
        for item in module_info:
            if item.endswith("widget.py"):
                main_file = module_info.get(item)
            # Get the module __init__ file if it exists
            if item == "__init__.py":
                module_init = module_info.get(item)

        # Check if the main file exists
        if not Path(main_file).exists():
            # Main file doesn't exist
            logger.warning(
                "Can not find the main file for module '%s'.", module_name)

        # Get the main class name from module_config.json
        module_class_name = module_info and module_info.get("class_name", None)
        if main_file and module_class_name:
            module = self.load_module_from_file(
                    module_name,
                    module_class_name,
                    main_file)

        # Let's try the init file(searching for the import of the main class)
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
                "Cannot import module via init file, file doesn't exist.")

        if not module and main_file:
            module_class_name = self.get_claass_name_from_all(main_file)
            if module_class_name:
                module = self.load_module_from_file(
                    module_name,
                    module_class_name,
                    main_file)

        # Init the module and return an instance
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
        """Get the class name from the '__all__' variable.

        Args:
        main_file (str)= file in which to look

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
        """Load the module from a file.

        Args:
        module_name (str)= name of the module(file)
        module_class_name (str)= name of the module's main class
        module_path (str)= path to the file containing the main class

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
                    "Cannot import module '%s' because: %s.",
                    module_name,
                    e)
                module = None
        else:
            logger.info("Module file name is '%s'.", module_name)
            logger.info("Module's class name is '%s'.", module_class_name)
            logger.info("Module file is at '%s'.", module_path)
            logger.error(
                "Cannot import module: missing arguments.")
        return module
