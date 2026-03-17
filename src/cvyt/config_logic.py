# -*- coding: utf-8 -*-
"""Operations on the config file/object"""
import logging
import re
from pathlib import Path

from cvyt.common import (convert_json_object_to_string,
                         convert_string_to_json_object)
from cvyt.default_app_config import DEFAULT_CONFIG

__all__ = ['ConfigLogic']

APP_CONFIG = 'app_config.json'

# Supported types
DEEPER_TYPES = (dict,)
SIMPLE_TYPES = (int, str, float, complex)
STR_TYPE = (str,)
FLAT_TYPES = (list,)
ALL_TYPES = SIMPLE_TYPES + DEEPER_TYPES + FLAT_TYPES

# Internal tags - config structure
ADVANCED_TAGS = {"advanced": "==>", "level_up": ".."}

# Supported advanced types - allowed by JSON
SUPPORT_ADVANCED = ["==>dict", "==>list", "==>set"]

# These types can be directly "Edited", "Added"
ADVANCED_TYPE_LIST = ["list"]
ADVANCED_TYPE_DICT = ["dict"]
ADVANCED_TYPE_NAME = ADVANCED_TYPE_DICT + ADVANCED_TYPE_LIST
SIMPLE_TYPES_NAME = ["string", "number"]
# Regex to indentify an index in key chain
INDEX_REGEX = r"\.{2}\d+"

# Available type names(shown via config UI)
AVAILABLE_VALUE_TYPE_NAMES = ADVANCED_TYPE_LIST + ADVANCED_TYPE_DICT \
    + SIMPLE_TYPES_NAME
# Convertion table - default type to UI name
AVAILABLE_VALUE_TYPE_TO_NAME = {
    "str": "string",
    "list": "list",
    "dict": "dict",
    "int": "number",
    "float": "number",
    "complex": "number"
}
# Help messages for each supported type
AVAILABLE_VALUE_TYPE_HELP = {
    "string": "A value of this type is stored as a string.",
    "list": "This type will result in storing an empty list.",
    "dict": "This type will result in storing an empty dict.",
    "number": "A value of this type is stored as a number."
}
# Level-up tags
LEVEL_UP = [".", ".."]
# Number - comparison purpose
CONVERT_NUMBER_TO = "number"

# Key(s)
UNKNOWN = "Unknown"
RESOLUTION_KEY = ["max_resolution"]
RESOLUTION_X_KEY = ["X"]
RESOLUTION_Y_KEY = ["Y"]
TITLE_KEY = ["title"]
NAME_KEY = ["name"]
VERSION_KEY = ["version"]
CONTACT_KEY = ["contact"]
HOMEPAGE_KEY = ["homepage"]
DESCRIPTION_KEY = ["description"]
# Get tags for config presentation - level up, advanced types(dict, list)
TAG_ADVANCED = ["config", "tags", "advanced"]
TAG_LEVEL_UP = ["config", "tags", "level_up"]

# Default messages for config change validation
NAME_MSG_ERROR_FILL = "The 'Name' has to be filled."
VALUE_MSG_ERROR_FILL = """
The 'Value' has to be filled with correct value(see 'Type')."""
TYPE_MSG_ERROR_FILL = "The 'Type' has to be filled."


logger = logging.getLogger(__name__)


class ConfigLogic():
    """Class for handling config file(JSON)."""
    def __init__(self, /, **kwargs):
        super().__init__()
        self.config_path = None
        self.config = None
        self.load_config(kwargs.get('config', APP_CONFIG))
        self.config_struct_tags = {}
        self.set_config_struct_tags_from_config()

    def get_name_for_type(self, type_name: str) -> str:
        """Convert a python type to its display name.

        Args:
        type_name (str)= name of the Python type

        Returns:
        Dispaly name of the type.
        """
        name = "string"
        if type_name and type_name in AVAILABLE_VALUE_TYPE_TO_NAME:
            name = AVAILABLE_VALUE_TYPE_TO_NAME.get(type_name, "string")
        return name

    def get_list_of_type_names(self) -> list:
        """Return a list of supported types/names."""
        return AVAILABLE_VALUE_TYPE_NAMES

    def get_config_object(self):
        """Return the config object."""
        return self.config

    def reload_config(self):
        """Reload the whole config object."""
        if self.config_path:
            self.load_config(self.config_path)

    def get_resolution(self) -> tuple:
        """Get resolution from the config file."""
        resolution_x_y = (None, None)
        if self.config and RESOLUTION_KEY:
            resolution = self.get_value_for_key(RESOLUTION_KEY)
            if resolution:
                try:
                    resolution_x_y = (resolution.get("X", 0),
                                      resolution.get("Y", 0))
                except Exception as e:
                    logger.error("Cannot get resolution because %s.", e)
                    resolution_x_y(None, None)
        return resolution_x_y

    def get_title(self) -> str:
        """Get the 'title' from the config file."""
        title = UNKNOWN
        if self.config and TITLE_KEY:
            title = self.get_value_for_key(TITLE_KEY)
        return title

    def get_name(self) -> str:
        """Get the 'name' from the config file."""
        name = UNKNOWN
        if self.config and NAME_KEY:
            name = self.get_value_for_key(NAME_KEY)
        return name

    def get_version(self) -> str:
        """Get the 'version' from the config file."""
        version = UNKNOWN
        if self.config and VERSION_KEY:
            version = self.get_value_for_key(VERSION_KEY)
        return version

    def get_contact(self) -> str:
        """Get the 'contact' from the config file."""
        contact = UNKNOWN
        if self.config and CONTACT_KEY:
            contact = self.get_value_for_key(CONTACT_KEY)
        return contact

    def get_homepage(self) -> str:
        """Get the 'homepage' from the config file."""
        homepage = UNKNOWN
        if self.config and HOMEPAGE_KEY:
            homepage = self.get_value_for_key(HOMEPAGE_KEY)
        return homepage

    def get_description(self) -> str:
        """Get the 'description' from the config file."""
        description = UNKNOWN
        if self.config and DESCRIPTION_KEY:
            description = self.get_value_for_key(DESCRIPTION_KEY)

        return description

    def get_value_type_help(self, type_name: str) -> str | None:
        """Get the help message for specified a type name.

        Args:
        type_name = name of the type

        Returns:
        Help message or None
        """
        message = None
        if type_name:
            message = AVAILABLE_VALUE_TYPE_HELP.get(type_name)

        return message

    def convert_value_to_type(self, type_name: str, value):
        """Convert a value to the specified type.

        Args:
        type_name (str)= name of the type
        value = value to convert

        Returns:
        Converted value
        """
        new_value = None
        # Advanced types - list, dict
        if type_name and type_name in ADVANCED_TYPE_DICT:
            new_value = {}
        elif type_name and type_name in ADVANCED_TYPE_LIST:
            new_value = []
        elif type_name and value:
            # Simple types - numbers
            if type_name == CONVERT_NUMBER_TO:
                re.sub(r"\ ", "", value)
                int_match = re.search(r"\d+", value)
                float_match = re.search(r"\d+[.]+\d+", value)
                complex_match = re.search(r"\d+[+]\d+[j]", value)
                # Int
                if int_match and int_match.group(0) == value:
                    new_value = int(value)
                # float
                if float_match and float_match.group(0) == value:
                    new_value = float(value)
                # complex
                if complex_match and complex_match.group(0) == value:
                    try:
                        new_value = str(complex(value))
                    except Exception as e:
                        logger.warning(
                            "Could not convert '%s' to a complex number(%s).",
                            value, e)
            else:
                new_value = value
        return new_value

    def load_config(self, config_file_name=APP_CONFIG):
        """Load app info + config.

        Args:
        config_file_name = name of config file
        """
        self.config_path = Path.cwd().joinpath(config_file_name)
        if self.config_path.exists():
            with open(str(self.config_path), "r", encoding="utf-8") as config:
                try:
                    self.config = convert_string_to_json_object(config.read())
                except Exception as e:
                    self.config = None
                    self.config_path = None
                    logger.error("Cannot load config content(%s).", e)
        else:
            try:
                # Config is not present, creating one with default content
                with open(
                        str(self.config_path),
                        "w",
                        encoding="utf-8") as config_out:
                    try:
                        config_out.write(convert_json_object_to_string(
                            DEFAULT_CONFIG))
                    except Exception as e:
                        logger.info(
                            "Cannot write to config file '%s'.",
                            self.config_path)
                        logger.error(
                            "Cannot write because '%s'.", e)
                # Read it, load it into variable
                with open(
                        str(self.config_path),
                        "r",
                        encoding="utf-8") as config_in:
                    try:
                        self.config = convert_string_to_json_object(
                            config_in.read()
                        )
                    except Exception as e:
                        logger.info(
                            "Cannot read the content of config file '%s'.",
                            self.config_path)
                        logger.error("Cannot read because '%s'.", e)
            except Exception as e:
                self.config = None
                logger.error(
                    "Attemp to create default config file failed(%s).", e)

    def save_config(self, path_to: str, name=None):
        """Save the current main config object to a specified file.

        Args:
        path_to (str)= path to the JSON file, where the config object\
                  will be stored in JSON format
        name = extra name to use(not required, name of file should be set)
        """
        saved = True
        store_to = path_to
        if name:
            store_to = str(Path(path_to).parent.joinpath(name))
        if self.config and Path(store_to).exists():
            # Set the original content as a backup
            original = None
            with open(str(store_to), "r", encoding="utf-8") as config_in:
                original = config_in.read()
            # Write new content to the output config file
            with open(str(store_to), "w", encoding="utf-8") as config_out:
                try:
                    config_out.write(convert_json_object_to_string(
                        self.config))
                except Exception as e:
                    config_out.write(original)
                    logger.error(
                        "Attempt to store the current config to the specified\
                        file failed(%s).", e)
                    saved = False
        else:
            logger.error(
                """No file to store in specified path or config object doesnt
                exist.""")
            saved = False
        return saved

    def set_config_object(self, config_object):
        """Set the current config object to a new object

        Args:
        config_object = the config object to use for replacing
                        the current config object(JSON)
        """
        if self.config and config_object \
                and isinstance(config_object, type(self.config)):
            self.config = config_object

    def check_key_in_level(self, key: str, level) -> bool:
        """Check if the key exists at the  given level of the config.

        Args:
        key (str)= key to check
        level = level at which to check

        Returns:
        True if the key exists, othervise False
        """
        return key in level

    def get_value_for_key(self, keys: list, index=None):
        """Get the value for a given key.

        Args:
        keys (list)= chain of keys to search for
        index = optional index if the searched value is a list.

        Returns:
        The value if the key exists, otherwise the original key.
        """
        key_search = keys
        key_search = key_search.pop(-1) if key_search and \
            key_search[-1] == '..' else key_search

        value = self.get_value_for_key_recursive(key_search, index=index)
        return value

    def get_value_for_key_recursive(self, keys: list, index=None):
        """Get the value for key, recursively.

        This function searches level by level until it finds the last key,
        then returns the corresponding value.

        Args:
        keys (list)= chain of keys
        index = optional(if the value is in the list/set/frozenset)

        Returns:
        Returns the value if successful, otherwise the original key.
        """
        level = self.config
        if keys and level:
            for key in keys:
                # Check if key is an index --> adjust it
                key_to_index = self.get_index_if_is(key)
                # Dict
                if isinstance(level, DEEPER_TYPES):
                    if self.check_key_in_level(key, level):
                        level = level[key]
                    else:
                        level = key
                # List
                elif isinstance(level, FLAT_TYPES):
                    # Now we can use the index to set/list/frozenset
                    if key_to_index is not None \
                            and len(level) >= key_to_index:
                        level = level[key_to_index]
                    elif index is not None and level and len(level) >= index:
                        level = level[index]
                    else:
                        level = key
                # str
                elif isinstance(level, str):
                    level = key
                # int, float, complex
                elif isinstance(level, (int, float, complex)):
                    # Its ok, not change
                    pass
                # Else
                else:
                    level = None
                    break
            return level
        else:
            # Return the root list of keys from the config, otherwise None
            try:
                return level
            except Exception:
                logger.error(
                    "Problem with getting list of keys from level '%s'.",
                    level.keys())
                return None

    def get_config_path(self) -> str | None:
        """Returns the path to the config file."""
        config_path = None
        if self.config_path:
            config_path = str(Path(self.config_path).absolute())
        return config_path

    def get_specified_type(self, items):
        """Return the type or shortcut based on the item type.

        This function takes a value and compares it against a list of supported
        (advanced) types that need to be converted to the shortcut format used
        by the UI. If the value is not an advanced type, the original value
        is returned.
        """
        if deeper := self.get_type_of_value_shortcut(items, DEEPER_TYPES):
            # dict
            return deeper
        elif simple := self.get_type_of_value_shortcut(items, FLAT_TYPES):
            # (list)
            return simple
        elif self.get_type_of_value_shortcut(items, SIMPLE_TYPES):
            # (int, str, float, complex)
            return items
        return "Uknown"

    @staticmethod
    def get_type_of_value_shortcut(value, types) -> str:
        """Get(creates) the shortcut for a value type.

        Args:
        value = value to be checked
        types = type for display

        Returns:
        Shortcut
        """
        shortcut = None
        if isinstance(value, types):
            shortcut = f"==>{type(value).__name__}"
        return shortcut

    def create_config_deep_path(self, parts: list) -> str:
        """Creates a path to a specific level of the config file.

        Used for the UI, where only string types are utilized.

        Args:
        parts (list)= list of keys

        Returns:
        Path in string format
        """
        return "/".join(parts)

    def go_level_up(self, last_key) -> bool:
        """Decide if the last_key is a key for moving up.

        Helps to decide whether to add the key to the keychain or not

        Args:
        last_key = the last clicked key(treewidget)

        Returns:
        True in case yes
        """
        level_up = False
        if last_key in LEVEL_UP:
            level_up = True
        return level_up

    def let_through(self, key, value) -> bool:
        """Determine if the given values are valid to continue.

        Args:
        key = key column from the config tree widget table
        value = value column from the config tree widget table

        Return:
        True if the values are valid, otherwise False
        """
        advanced = ADVANCED_TAGS.get('advanced', None)
        level_up = ADVANCED_TAGS.get('level_up', None)

        if advanced and level_up:
            return (
                    value != advanced
                    and
                    (key.startswith(level_up)
                     or
                     value.startswith(advanced)))
        else:
            return False

    def get_config_struct_tags_dict(self) -> dict:
        """Get the struct tags object."""
        return self.config_struct_tags

    def set_config_struct_tags_from_config(self):
        """Get the struct tags from the config file."""
        # Tags for more advanced types(dict, list, frozenset, set)
        if self.config:
            self.config_struct_tags["advanced"] = \
                self.get_value_for_key(TAG_ADVANCED)
            self.config_struct_tags["level_up"] = \
                self.get_value_for_key(TAG_LEVEL_UP)

    def is_advanced_type(self, name: str) -> bool:
        """Check if the given name is in the list of advanced types.

        Params:
        name (str)= name of the type

        Returns:
        True if the type is an advanced type, otherwise False
        """
        advanced = False
        if name:
            if name in SUPPORT_ADVANCED:
                advanced = True
        return advanced

    def get_index_if_is(self, key) -> int | None:
        """Check if the given key is in index form. If it is,
        returns the index.

        Params:
        key = the key to check

        Returns:
        The index if the key is in index format, otherwise None.
        """
        if re.search(INDEX_REGEX, key):
            parts = key.split("..")[-1]
            try:
                return int(parts[-1])
            except Exception as e:
                logger.error(
                    "It's not a valid index in the config file %s.", e)
        return None

    def can_i_edit_object_of_type(self, object_type: str) -> bool:
        """Check if a specific type can be edited.

        Args:
        object_type (str)= name of the type

        Returns:
        True if can be, otherwise False
        """
        edit = True
        if object_type and object_type in ADVANCED_TYPE_NAME:
            edit = False
        return edit

    def can_i_apply_changed(
            self, name: str, value, value_type: str, apply_to: str) -> tuple:
        """Check if changes can be applied based on the input and its types

        Args:
        name (str)= name/key
        value = value
        value_type (str)= type(name) of value
        apply_to (str)= can I apply changes to specific type

        Returns:
        can_apply = True if changes can be, otherwise False
        name_msg = message related to 'name'
        value_msg = message related to 'value'
        type_msg = message related to 'type'
        """
        can_apply = True
        name_msg = ""
        value_msg = ""
        type_msg = ""
        if not value_type:
            type_msg = TYPE_MSG_ERROR_FILL
            can_apply = False
        if apply_to in ADVANCED_TYPE_LIST:
            # list
            if value is None and value_type \
                    not in ADVANCED_TYPE_NAME:
                value_msg = VALUE_MSG_ERROR_FILL
                can_apply = False
            if not value_type:
                type_msg = TYPE_MSG_ERROR_FILL
                can_apply = False
        elif apply_to in ADVANCED_TYPE_DICT:
            # dict
            if not name and value_type not in ADVANCED_TYPE_NAME:
                name_msg = NAME_MSG_ERROR_FILL
                can_apply = False
            if value is None and value_type not in ADVANCED_TYPE_NAME:
                value_msg = VALUE_MSG_ERROR_FILL
                can_apply = False
            if not name and value_type in ADVANCED_TYPE_NAME:
                value_msg = VALUE_MSG_ERROR_FILL
                can_apply = False
            if not value_type:
                type_msg = TYPE_MSG_ERROR_FILL
                can_apply = False
        elif apply_to and apply_to in SIMPLE_TYPES_NAME:
            # string, number
            if value is None:
                value_msg = VALUE_MSG_ERROR_FILL
                can_apply = False
            if not value_type:
                type_msg = TYPE_MSG_ERROR_FILL
                can_apply = False
        return (can_apply, name_msg, value_msg, type_msg)

    def get_list_of_keys(self, level=[]) -> tuple:
        """Use given chain of keys to search inside the config object.

        Find all valid key+value pairs and conver them to the format used
        by UI.

        Args:
        level (list)= list of keys in list format, in left to right order.
                1. If list is empty --> root level of the config file is used
                2. If not empty --> recursively traverse the config file and 
                                    return value at that level

        Returns:
        A tuple
        - lines (list): List of converted key-value pairs in the UI format.
        - key_chain (list): Chain of keys to reach this level inside the
                            config.
        """
        # Internal variables
        _previous_values = []
        _values_out = []
        _valid_level = []

        # Root level
        if len(level) == 0:
            # Root level
            root_keys = self.get_value_for_key(None)
            for key in root_keys:
                value = self.get_value_for_key([key])
                value_type = self.get_specified_type(value)
                _values_out += [("|-" + str(key), value if
                                not value_type else value_type)]
            # Add the current level
            _values_out.insert(0, (".", "."))
        else:
            # Advance structure
            for key in level:
                index = self.get_index_if_is(key)
                if key != "..":
                    _valid_level.append(key)
                    new_key = _valid_level
                    items = self.get_value_for_key(new_key, index)
                    if items is not None:
                        _previous_values.append(items)
                    if len(_previous_values) > 1:
                        _previous_values.pop(0)

            # Not a root level
            if len(_previous_values) >= 1:
                previous = []
                while _previous_values:
                    _previous_value = _previous_values.pop(-1)
                    if self.get_type_of_value_shortcut(
                            _previous_value, DEEPER_TYPES):
                        if _previous_value:
                            # dict - not empty
                            for deeper_key in _previous_value:
                                value = self.get_specified_type(
                                    _previous_value[deeper_key])
                                previous.append(("|-" + deeper_key, value))
                        else:
                            break
                    elif self.get_type_of_value_shortcut(
                            _previous_value, SIMPLE_TYPES):
                        # int, str, float, complex,
                        previous.append(
                            ("|-" + str(_previous_value),
                             str(_previous_value)))
                    elif self.get_type_of_value_shortcut(
                            _previous_value, FLAT_TYPES):
                        if _previous_value:
                            for index, simple_item in \
                                    enumerate(_previous_value):
                                value = self.get_specified_type(
                                    simple_item)
                                new_key = value
                                if self.is_advanced_type(value):
                                    new_key = ".." + str(index)
                                # Every key has to be string
                                previous.append(("|-" + str(new_key), value))
                        else:
                            break

                # Insert the "level up" tag
                previous.insert(0, ("|-..", ".."))
                _values_out += previous
            else:
                # Show the root level
                _values_out = []
                root_keys = self.get_value_for_key(None)
                for key in root_keys:
                    value = self.get_value_for_key([key])
                    value_type = self.get_specified_type(value)
                    _values_out += [("|-" + str(key), value if
                                    not value_type else value_type)]
                # Add the current level to the root overview
                _values_out.insert(0, (".", "."))
        return (_values_out, _valid_level)

    def apply_to_config(
            self,
            keys_chain,
            remove=False,
            edit=None,
            add=None,
            item_index=None) -> bool:
        """Apply the required changes to the config object.

        Supports:
        remove = remove the specified item
        edit = alter the selected item
        add = add a new item at the  specified position in the config object

        Args:
        keys_chain = chain of keys --> to reach the level where the changes
                     should be applied
        remove = tag signaling to remove an item(True or False)
        edit = tuple of (key, value) to alter an existing item
        add = tuple of (key, value) to add a new item
        item_index = index in case changes are applied over a list.

        Returns:
        True if changes were applied successfully, otherwise False
        """
        applied = True
        try:
            # We have a chain of keys and a config to be altered
            if keys_chain and self.config:
                # Store the level where changes should be applied
                apply_object, apply_object_key = None, None
                # Start searching the root level
                working_list = [self.config]
                while working_list:
                    # Start from the first key
                    for watch_key in keys_chain:
                        # Is this key an index? Format: '..1',
                        index = self.get_index_if_is(watch_key)
                        # Get the item from the list of search items
                        current_item = working_list.pop()
                        if isinstance(current_item,
                                      FLAT_TYPES):
                            # List
                            keys_match = [match_key for match_key
                                          in current_item
                                          if match_key == watch_key]
                            # Match to our key
                            if keys_match:
                                apply_object = current_item
                                apply_object_key = watch_key
                                if item_index is not None\
                                        and len(current_item) >= item_index:
                                    apply_object_key = item_index
                                    apply_object = current_item
                                else:
                                    apply_object_key = current_item.index(
                                        watch_key)
                                    apply_object = current_item
                                working_list.append(current_item)
                            elif index is not None \
                                    and len(current_item) >= index:
                                # No match, try index(from chain of keys)
                                index_value = current_item[index]
                                apply_object_key = index
                                apply_object = current_item
                                working_list.append(index_value)
                            elif item_index is not None \
                                    and len(current_item) >= item_index:
                                # No match, not a valid index, try item_index
                                index_value = current_item[item_index]
                                apply_object_key = item_index
                                apply_object = current_item
                                working_list.append(index_value)

                        elif isinstance(current_item, DEEPER_TYPES):
                            # Dict
                            keys_match = [match_key for match_key, _
                                          in current_item.items()
                                          if match_key == watch_key]
                            # Match key
                            if keys_match:
                                # Iterate through it
                                for key_current, value_current in \
                                        current_item.items():
                                    # Match on key, store the final
                                    # level+key and add it to the search list.
                                    if key_current in keys_match:
                                        apply_object = current_item
                                        apply_object_key = watch_key
                                        working_list.append(value_current)
                                        break
                        else:
                            # int, float, str, bool, tuple, complex
                            current_item = working_list
                            keys_match = [match_key for match_key
                                          in current_item
                                          if match_key == watch_key]
                            # match?
                            if keys_match:
                                apply_object = current_item
                                apply_object_key = watch_key
                                break
                    break
                # Ok, all keys from chain of keys
                if apply_object and apply_object_key is not None:
                    # Apply changes here
                    if remove:
                        # Remove
                        try:
                            del apply_object[apply_object_key]
                        except Exception as e:
                            logger.error(
                                "Problem removing something from the config\
                                object/structure(%s).", e)
                            applied = False
                    elif edit is not None:
                        # Strip - key and value - remove empty trailing chars
                        edit_key = edit[0].strip()
                        # Check if it can be stripped, if not keep, the
                        # original
                        edit_value = edit[1]
                        if isinstance(edit, STR_TYPE):
                            edit_value = edit[1].strip()
                        # Edit
                        if None not in edit:
                            # Edit items
                            try:
                                if isinstance(
                                        apply_object,
                                        FLAT_TYPES
                                        ):
                                    apply_object[apply_object_key] = edit_value
                                elif isinstance(
                                        apply_object,
                                        DEEPER_TYPES
                                        ):
                                    # Dict
                                    if apply_object_key != edit_key:
                                        # The key is different
                                        del apply_object[apply_object_key]

                                        apply_object[edit_key] = edit_value
                                    elif apply_object_key == edit[0]:
                                        # The key is the same, just replace the
                                        # value
                                        apply_object[edit_key] = edit_value
                                else:
                                    apply_object[apply_object_key] = edit_value
                            except Exception as e:
                                logger.error(
                                    "Problem editing something in the config\
                                    object/structure(%s).", e)
                                applied = False
                        else:
                            logger.error(
                                """Cannot edit item in config.
                                Some attributes are missing '%s'.""", add)
                            applied = False
                    elif add is not None:
                        # Strip - key and value - removing empty trailing chars
                        add_key = add[0].strip()
                        # Check if it can be stripped, if not, keep the
                        # original
                        add_value = add[1]
                        if isinstance(add[1], STR_TYPE):
                            add_value = add[1].strip()
                        # Add the new item
                        if None not in add:
                            # Add the items
                            try:
                                if isinstance(
                                        apply_object[apply_object_key],
                                        FLAT_TYPES
                                        ):
                                    # list
                                    apply_object[apply_object_key].append(
                                        add_value)
                                elif isinstance(
                                        apply_object[apply_object_key],
                                        DEEPER_TYPES
                                        ):
                                    # Dict
                                    apply_object[apply_object_key][add_key] = \
                                        add_value
                                else:
                                    logger.warning(
                                        """Cannot add item '%s' to the config
                                        file, unknown type.""", add)
                                    applied = False
                            except Exception as e:
                                logger.error(
                                    """Problem adding something to the config
                                    object/structure(%s).""", e)
                                applied = False
                        else:
                            logger.error(
                                """Cannot add item to config.
                                Some attributes are missing '%s'.""", add)
                            applied = False

            elif not keys_chain and self.config:
                # The root level
                if add:
                    add_key = add[0].strip()
                    # Check if it can be stripped, if not, keep the original
                    add_value = add[1]
                    if isinstance(add[1], STR_TYPE):
                        add_value = add[1].strip()
                    # Only add if possible
                    config = self.config
                    config[add_key] = add_value
                else:
                    # Nothing else
                    logger.error(
                        "Nothing selected to be remove/edited."
                    )
                    applied = False
        except Exception as e:
            # Problem
            logger.error(
                "Trying to apply changes to the config file failed(%s).", e)
            applied = False
        return applied
