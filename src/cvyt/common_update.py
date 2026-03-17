# -*- coding: utf-8 -*-
"""Update methods used by the update widget and the available modules model."""

import glob
import logging
import re
from pathlib import Path

from cvyt.common import convert_string_to_json_object

# Key chains to retrieve specific values from a config file.
# You can think of this as a path.
# For example:
#   modules/root --> ["modules", "root"]
#   {"modules": {"root": "modules"}} 
MODULES_ROOT_PATH = ["modules", "root"]
MODULE_CONFIG_FILE_NAME = ["modules", "config"]
MODULES_REQUIRED_CONTENT = ["modules", "required"]
# Names of folders used internally:
# MODULES_FOLDER = "modules"
# Temporary folder used during updatee
TEMP_FOLDER = "temp_update"
# Regex to filter main widget files: '*widget.py'
WIDGET_REGEX = "(.*)config.json"


__all__ = ['CommonUpdate']


logger = logging.getLogger(__name__)


class CommonUpdate():
    """Common update methods."""
    def __init__(self, /, **kwargs):
        self.config = kwargs.get('config', None)
        self.available_modules = {}

    def get_available_modules(self):
        """Gets and returns the name of the founded module and
        info about it."""
        for name in self.available_modules:
            yield (name, self.available_modules[name])

    def get_count_of_available_modules(self):
        """Get the number of available modules."""
        return len(self.available_modules) if self.available_modules else 0

    def get_value_for_key(self, module_name: str, key: str):
        """Get the value for a key in the given module.

        Args:
        name_module (str)= the name of the module to search in
        key (str)= the key to search for

        Returns:
        value or None
        """
        value = None
        # Get the module
        module = self.available_modules.get(module_name, None)
        # We have the module, let's get the value
        value = module.get(key, None) if module else None
        return value

    def set_value_for_key(self, module_name: str, key: str, value):
        """Set the value for a key in the given module.

        Args:
        module_name (str)= the name of the module to search in
        key (str)= the key to search for
        value = the value to store
        """
        # Get the module
        module = self.available_modules.get(module_name, None)
        # The module and key are found, now set the value
        if module and key in module:
            module[key] = value

    def get_modules_root_path(self) -> str:
        """Get the path to the modules folder."""
        root_key = self.config and self.config.get_value_for_key(
            self.get_modules_root_keys_chain())
        return root_key if root_key else ""

    def get_module(self, module_name: str):
        """Get the module object.

        Args:
        module_name (str)= the name of the module
        """
        module = None
        if module_name:
            module = self.available_modules.get(module_name, None)
        return module

    def get_required_files(self, key: list) -> list:
        """Get a list of required file, folders for a specific update.

        Args:
        key (list)= the key to get the list of required files

        Returns:
        List of required files
        """
        required_files = self.config and self.config.get_value_for_key(
                       key)
        required = []
        # The required part is a list
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
        """Creates an update list of availble modules.

        Args:
        folder (str)= where to search for modules
        """
        required = self.get_required_module_content_keys_chain()

        files = self.check_valid_content(
            Path(folder) if folder else "",
            required
        )

        if files:
            # Get the path to the config file
            config_file = [str(file) for file in files if re.search(
                WIDGET_REGEX, file)]
            # Create a module info object
            self.create_info_object_about_module(
                Path(folder).name, config_file)
            # Add the rest of required info
            self.add_rest_of_required_info(
                Path(folder).name
            )
        else:
            module_folders = self.get_only_folders_from_root_folder(
                                str(folder))
            for module_folder in module_folders:
                self.create_update_list(Path(module_folder))

    def get_only_folders_from_root_folder(self, root: str = None) -> list:
        """Get a list of folders on the root level.

        Args:
        root (str)= the folder to search for subfolders

        Returns:
        List of folders
        """
        root_folders = []
        if root and Path(root).exists():
            # Folders only
            root_folders = ([i for i in Path(root).iterdir()
                            if Path.is_dir(i)])
        return root_folders

    def get_detailed_info_about_module(
            self,
            name: str,
            ) -> dict:
        """Get detailed info about the module.

        This is a lazy approach, so the information is not kept in memory.

        Args:
        name (str)= the name of the module

        Returns:
        a dict with info or None
        """
        # Module info
        module_info = {}
        # Get the root folder for the module
        if name and name in self.available_modules:
            # Get the required files again
            required = self.get_required_module_content_keys_chain()
            # Retrive the rest
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
        """Create simple info object(dict) about the module.

        Args:
        name (str)= the name of module
        config_file (list)= the path to the configuration file(list)
        """
        if name and config_file and name not in self.available_modules:
            self.available_modules[name] = {}
            self.available_modules[name][Path(config_file[0]).name] =\
                config_file[0]

    def check_valid_content(self, folder: Path, keys: list) -> list:
        """Check if the given folder contains all required files for a
        valid module folder.

        Args:
        folder = the path to the folder to check
        keys = the chain of keys

        Returns:
        a list of valid files(paths) for module
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
                    # The correct level --> check
                    files = [item for item in founded
                             if item.endswith(require)]
                    # Just to be sure :)
                    try:
                        files_regex = [item for item in founded
                                       if re.match(require,
                                                   str(Path(item).name))]
                    except Exception as e:
                        logger.warning(
                            """Problem checking valid content against required:
                            '%s' due to: %s.""",
                            require, e)
                if files:
                    valid_folder += files
                if not files and files_regex:
                    valid_folder += files_regex
            # Required == found
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
        """ Add or find the remaining required information.

        Args:
        name = the name of update part to process
        """
        if name in self.available_modules:
            self.process_basic_info(
                name
            )

    def process_basic_info(self, name):
        """Processes basic info about the module and stores it.

        Finds and stores info such as the name, root folde path,
        description, etc. Stores it in a dict object.

        Args:
        name = the name of the module
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
                            # Retrieve the main class name of the module.
                            # (e.g. SplitToFrames)
                            module["class_name"] = config_content.get(
                                                "class_name",
                                                None)
                except Exception as e:
                    logger.error(
                        """There was a problem gathering information about the
                        module '%s' (%s).""",
                        name, e)
                root_path = Path(config_file[0]).parent
                module["root"] = str(root_path)
                # Name derived from the folder
                module["name"] = name
                # Update - default is True
                module["update"] = True

    # Simple methods to retrieve static variables
    def get_modules_root_keys_chain(self):
        """# Returns a chain of keys to search the config file for the module
        root."""
        return MODULES_ROOT_PATH

    def get_modules_config_file_name_keys_chain(self):
        """Returns a chain of keys to search the config file for the config
        file name."""
        return MODULE_CONFIG_FILE_NAME

    def get_temp_folder_name(self):
        """Returns the temporary folder name for processing module updates."""
        return TEMP_FOLDER

    def get_required_module_content_keys_chain(self):
        """Returns a chain of keys to search the config file for the list of
        required files."""
        return MODULES_REQUIRED_CONTENT
