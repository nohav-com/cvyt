# -*- coding: utf-8 -*-
"""Update methods used by update widget, available modules model."""

import glob
import logging
import re
from pathlib import Path

from cvyt.common import convert_string_to_json_object

# Keys chains to get specific value from config file
# You can inagine this as path.
# e.g. modules/root --> ["modules", "root"]
# e.g. {"modules" : {"root": "modules"}}
MODULES_ROOT_PATH = ["modules", "root"]
MODULE_CONFIG_FILE_NAME = ["modules", "config"]
MODULES_REQUIRED_CONTENT = ["modules", "required"]
# Names of folder used internally
# MODULES_FOLDER = "modules"
# Temp folder used during update
TEMP_FOLDER = "temp_update"
# Regex for filtering main widget folder = '*widget.py'
WIDGET_REGEX = "(.*)config.json"


__all__ = ['CommonUpdate']


logger = logging.getLogger(__name__)


class CommonUpdate():
    """Common update methods."""
    def __init__(self, /, **kwargs):
        self.config = kwargs.get('config', None)
        self.available_modules = {}

    def get_available_modules(self):
        """Gets and return name of founded module and info about it."""
        for name in self.available_modules:
            yield (name, self.available_modules[name])

    def get_count_of_available_modules(self):
        """Get number of available modules."""
        return len(self.available_modules) if self.available_modules else 0

    def get_value_for_key(self, module_name: str, key: str):
        """Get value for key in specific module.

        Args:
        name_module = name of the module to search in
        key = key to search for

        Returns:
        value or None
        """
        value = None
        # Get module
        module = self.available_modules.get(module_name, None)
        # We have module, lets get value
        value = module.get(key, None) if module else None
        return value

    def set_value_for_key(self, module_name: str, key: str, value):
        """Set value for key in specific module.

        Args:
        module_name = name of the module to search in
        key = key to search for
        value = value to store
        """
        # Get module
        module = self.available_modules.get(module_name, None)
        # We have module and key is in this module, set value
        if module and key in module:
            module[key] = value

    def get_modules_root_path(self) -> str:
        """Get path to modules folder."""
        root_key = self.config and self.config.get_value_for_key(
            self.get_modules_root_keys_chain())
        return root_key if root_key else ""

    def get_module(self, module_name: str):
        """Get module object.

        Args:
        module_name = name of module
        """
        module = None
        if module_name:
            module = self.available_modules.get(module_name, None)
        return module

    def get_required_files(self, key: list) -> list:
        """Get list of required file, folders for specific update.

        Args:
        key = key to get list of required files

        Returns:
        List of required files
        """
        required_files = self.config and self.config.get_value_for_key(
                       key)
        required = []
        # Required part is list
        if isinstance(required_files, list):
            # Go deeper
            for file in required_files:
                required.append(self.config.get_value_for_key([file]))
        else:
            required = self.config and self.config.get_value_for_key(
                [required_files]
            )
        return required if required else []

    def create_update_list(self, folder: str):
        """Creates update list of availble modules.

        Args:
        folder = where to search for modules
        """
        required = self.get_required_module_content_keys_chain()

        files = self.check_valid_content(
            Path(folder) if folder else "",
            required
        )

        if files:
            # Get config file path
            config_file = [str(file) for file in files if re.search(
                WIDGET_REGEX, file)]
            # Create module info object
            self.create_info_object_about_module(
                Path(folder).name, config_file)
            # Add Rest of required info
            self.add_rest_of_required_info(
                Path(folder).name
            )
        else:
            module_folders = self.get_only_folders_from_root_folder(
                                str(folder))
            for module_folder in module_folders:
                self.create_update_list(Path(module_folder))

    def get_only_folders_from_root_folder(self, root=None) -> list:
        """Get list of folders on root level.

        Args:
        root = folder where to get list of folders

        Returns:
        List of folders
        """
        root_folders = []
        if root and Path(root).exists():
            # All folders - only
            root_folders = ([i for i in Path(root).iterdir()
                            if Path.is_dir(i)])
        return root_folders

    def get_detailed_info_about_module(
            self,
            name,
            ) -> dict:
        """Get detailed info about module.

        Lazy approach, not keeping that info in memory.

        Args:
        name = name of the module

        Returns:
        dict with info or None
        """
        # Module_info
        module_info = {}
        # Get root folder for module
        if name and name in self.available_modules:
            # Get required files again
            required = self.get_required_module_content_keys_chain()
            # Get rest of the module info
            module_folder = self.available_modules[name].get("root", None)
            if module_folder:
                files = self.check_valid_content(
                    Path(module_folder) if module_folder else "",
                    required
                )
                if files:
                    for file in files:
                        module_info[Path(file).name] = str(file)
        return module_info

    def create_info_object_about_module(self, name: str, config_file: list):
        """Create simple inof object(dict) about module.add()

        Args:
        name: = name of module
        config_file == path to configuration file(list)
        """
        if name and config_file and name not in self.available_modules:
            self.available_modules[name] = {}
            self.available_modules[name][Path(config_file[0]).name] =\
                config_file[0]

    def check_valid_content(self, folder: Path, keys: list) -> list:
        """Check if given folder containts everything it suppose to for
        valid module folder.

        Args:
        folder = path to folder to check
        keys = chain of keys

        Returns:
        list of valid files(paths) for module
        """
        required = self.get_required_files(keys)
        valid_folder = []
        if folder and folder.exists():
            founded = glob.glob(str(folder.joinpath('*')))
            for require in required:
                files = []
                files_regex = []

                # Need to go deeper
                if Path(require).name != require:
                    for item in founded:
                        if require.startswith(Path(item).name):
                            new_file_path = Path(item).parent.joinpath(require)
                            if new_file_path.exists():
                                files = [new_file_path]
                else:
                    # Right level -->check
                    files = [item for item in founded
                             if item.endswith(require)]
                    # Just to be sure :)
                    try:
                        files_regex = [item for item in founded
                                       if re.match(require,
                                                   str(Path(item).name))]
                    except Exception as e:
                        logger.warning(
                            "Problem with check valid content with required: '%s' because %s.",
                            require, e)
                if files:
                    valid_folder += files
                if not files and files_regex:
                    valid_folder += files_regex
            # Required == founded
            if len(required) != len(valid_folder):
                valid_folder = []
            else:
                for rest in glob.glob(str(folder.joinpath('**/*')),
                                      recursive=True):
                    if rest not in valid_folder:
                        valid_folder.append(rest)
        return valid_folder

    def add_rest_of_required_info(
            self, name):
        """Add/find rest of required info

        Args:
        name = Name of update part to process
        """
        if name in self.available_modules:
            self.process_basic_info(
                name
            )

    def process_basic_info(self, name):
        """Processes basic info about module and store it.

        Finds and stores info such name, root folde path,
        description, etc. Stores it to dict object.

        Args:
        name = name of the module
        """
        if name in self.available_modules:
            config_file = [self.available_modules[name][item]
                           for item in self.available_modules[name]
                           if isinstance(item, str)
                           and str(self.available_modules[name][item])
                           .lower().endswith('module_config.json')
                           ]
            # Module
            module = self.available_modules[name]
            if len(config_file) > 0 and Path(config_file[0]).exists():
                try:
                    with open(config_file[0], "r", encoding="utf-8") as config:
                        config_content = convert_string_to_json_object(
                            config.read())
                        if config_content:
                            module["description"] = config_content.get(
                                                    "description",
                                                    name)
                            # Get module class name - main class
                            # (e.g. SplitToFrames)
                            module["class_name"] = config_content.get(
                                                "class_name",
                                                None)
                except Exception as e:
                    logger.error(
                        "Problem with gathering info about module '%s' (%s).",
                        name, e)
                root_path = Path(config_file[0]).parent
                module["root"] = str(root_path)
                # Name - deriveted from folder
                module["name"] = name
                # Update - default is True
                module["update"] = True

    # Simple methods to get static variables
    def get_modules_root_keys_chain(self):
        """Returns chain of keys to search config file for modules root."""
        return MODULES_ROOT_PATH

    def get_modules_config_file_name_keys_chain(self):
        """Returns chain of keys to search config file for config file name."""
        return MODULE_CONFIG_FILE_NAME

    def get_temp_folder_name(self):
        """Returns temp folder name for update modules processing."""
        return TEMP_FOLDER

    def get_required_module_content_keys_chain(self):
        """Returns chain of keys to search config file for list of
        required files."""
        return MODULES_REQUIRED_CONTENT
