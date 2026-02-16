# -*- coding: utf-8 -*-
"""Operations over config file/object"""
import logging
import re
from pathlib import Path

from cvyt.common import (convert_json_object_to_string,
                         convert_string_to_json_object)
from cvyt.default_app_config import DEFAULT_CONFIG

__all__ = ['ConfigLogic']

APP_CONFIG = 'app_config.json'

# Suported types
DEEPER_TYPES = (dict,)
SIMPLE_TYPES = (int, str, float, complex)
STR_TYPE = (str,)
FLAT_TYPES = (list,)
ALL_TYPES = SIMPLE_TYPES + DEEPER_TYPES + FLAT_TYPES

# Internal tags - config structure
ADVANCED_TAGS = {"advanced": "==>", "level_up": ".."}

# Supported advanced types - allowed by json
SUPPORT_ADVANCED = ["==>dict", "==>list", "==>set"]

# These type can be "Edit", "Add" directly
ADVANCED_TYPE_LIST = ["list"]
ADVANCED_TYPE_DICT = ["dict"]
ADVANCED_TYPE_NAME = ADVANCED_TYPE_DICT + ADVANCED_TYPE_LIST
SIMPLE_TYPES_NAME = ["string", "number"]
# Regex to indentify index in keys chain
INDEX_REGEX = r"\.{2}\d+"

# Available type names(shown via config UI)
AVAILABLE_VALUE_TYPE_NAMES = ADVANCED_TYPE_LIST + ADVANCED_TYPE_DICT \
    + SIMPLE_TYPES_NAME
# Convertion table default type to UI name
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
    "string": "Value of this type will be stored as string.",
    "list": "This type will lead to store empty list.",
    "dict": "This type will lead to store empty dict",
    "number": "Value of this type will be stored as number."
}
# Level up tags
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
# Get tags for config presentation - level up, advanced type(dict, list)
TAG_ADVANCED = ["config", "tags", "advanced"]
TAG_LEVEL_UP = ["config", "tags", "level_up"]

# Default messages related to validation of config changes
NAME_MSG_ERROR_FILL = "The 'Name'  has to be filled."
VALUE_MSG_ERROR_FILL = """
The 'Value' has to be filled with correct value(see 'Type')."""
TYPE_MSG_ERROR_FILL = "The 'Type' has to be filled."


logger = logging.getLogger(__name__)


class ConfigLogic():
    """Class handling config file(json)."""
    def __init__(self, /, **kwargs):
        super().__init__()
        self.config_path = None
        self.config = None
        self.load_config(kwargs.get('config', APP_CONFIG))
        self.config_struct_tags = {}
        self.set_config_struct_tags_from_config()

    def get_name_for_type(self, type_name: str) -> str:
        """Convert python type to name.

        Args:
        type_name = name of the type(python name)

        Returns:
        Name of the type(presentation name). Default is string.
        """
        name = "string"
        if type_name and type_name in AVAILABLE_VALUE_TYPE_TO_NAME:
            name = AVAILABLE_VALUE_TYPE_TO_NAME.get(type_name, "string")
        return name

    def get_list_of_type_names(self) -> list:
        """Return list of supported types(names)."""
        return AVAILABLE_VALUE_TYPE_NAMES

    def get_config_object(self):
        """Return config object."""
        return self.config

    def reload_config(self):
        """Reload the whole config object."""
        if self.config_path:
            self.load_config(self.config_path)

    def get_resolution(self) -> tuple:
        """Get resoluiton from config file."""
        resolution_x_y = (None, None)
        if self.config and RESOLUTION_KEY:
            resolution = self.get_value_for_key(RESOLUTION_KEY)
            if resolution:
                try:
                    resolution_x_y = (resolution.get("X", 0),
                                      resolution.get("Y", 0))
                except Exception as e:
                    logger.error("Cannot get resolution because %s", e)
                    resolution_x_y(None, None)
        return resolution_x_y

    def get_title(self) -> str:
        """Get 'title' from config file."""
        title = UNKNOWN
        if self.config and TITLE_KEY:
            title = self.get_value_for_key(TITLE_KEY)
        return title

    def get_name(self) -> str:
        """Get 'name' form config file."""
        name = UNKNOWN
        if self.config and NAME_KEY:
            name = self.get_value_for_key(NAME_KEY)
        return name

    def get_version(self) -> str:
        """Get 'version' from config file."""
        version = UNKNOWN
        if self.config and VERSION_KEY:
            version = self.get_value_for_key(VERSION_KEY)
        return version

    def get_contact(self) -> str:
        """Get 'contact' from config file."""
        contact = UNKNOWN
        if self.config and CONTACT_KEY:
            contact = self.get_value_for_key(CONTACT_KEY)
        return contact

    def get_homepage(self) -> str:
        """Get 'homepage' from config file."""
        homepage = UNKNOWN
        if self.config and HOMEPAGE_KEY:
            homepage = self.get_value_for_key(HOMEPAGE_KEY)
        return homepage

    def get_description(self) -> str:
        """Get 'description' form config file."""
        description = UNKNOWN
        if self.config and DESCRIPTION_KEY:
            description = self.get_value_for_key(DESCRIPTION_KEY)

        return description

    def get_value_type_help(self, type_name: str) -> str | None:
        """Get help message for specified type name.add()

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
        """Convert value to given type.

        Args:
        type_name = name of type
        value = value to convert

        Returns:
        Converted value
        """
        new_value = None
        # Advanced types list, dict
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
                            "Could not convert '%s' to complex number(%s)."
                            , value, e)
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
                # Config is not present, lets create on with default content
                with open(
                        str(self.config_path),
                        "w",
                        encoding="utf-8") as config_out:
                    try:
                        config_out.write(convert_json_object_to_string(
                            DEFAULT_CONFIG))
                    except Exception as e:
                        logger.info(
                            "Can not write to config file '%s'.",
                            self.config_path)
                        logger.error(
                            "Can not write because '%s'.", e)
                # Read it, load it to variable
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
                            "Can not read content of config file '%s'.",
                            self.config_path)
                        logger.error("Can not read because '%s'.", e)
            except Exception as e:
                self.config = None
                logger.error(
                    "Attemp to create default config file failed(%s).", e)

    def save_config(self, path_to: str, name=None):
        """Save current main config object to specified file.

        Args:
        path_to = path to json file, where the config object\
                  in json format will be stored
        name = extra name to use(not required, name of file should be set)
        """
        saved = True
        store_to = path_to
        if name:
            store_to = str(Path(path_to).parent.joinpath(name))
        if self.config and Path(store_to).exists():
            # Get original content as backup
            original = None
            with open(str(store_to), "r", encoding="utf-8") as config_in:
                original = config_in.read()
            # Lets write new content to outpu config file
            with open(str(store_to), "w", encoding="utf-8") as config_out:
                try:
                    config_out.write(convert_json_object_to_string(
                        self.config))
                except Exception as e:
                    config_out.write(original)
                    logger.error(
                        "Attempt to store current config to specified file \
                        failed(%s).", e)
                    saved = False
        else:
            logger.error(
                "No file to store in filled or config object doesnt exist.")
            saved = False
        return saved

    def set_config_object(self, config_object):
        """Set current config object to new object

        Args:
        config_object = config object to use for replacing
                        the current config object(json)
        """
        if self.config and config_object \
                and isinstance(config_object, type(self.config)):
            self.config = config_object

    def check_key_in_level(self, key: str, level) -> bool:
        """Check if key is given level of config.

        Args:
        key = key to check
        level = level where to check

        Returns:
        True in case yes, othervise False
        """
        return key in level

    def get_value_for_key(self, keys: list, index=None):
        """Get value for key.

        Args:
        keys = chain(list) of keys to search for
        index = optional args in case that search value
                is list(index to this list)

        Returns:
        In case of success returns the value, otherwise the original key.
        """
        key_search = keys
        key_search = key_search.pop(-1) if key_search and \
            key_search[-1] == '..' else key_search

        value = self.get_value_for_key_recursive(key_search, index=index)
        return value

    def get_value_for_key_recursive(self, keys: list, index=None):
        """Get value for key, recursively.

        Goes through level by level until it find the last key,
        than returns value.

        Args:
        keys = chain(list) of keys
        index = optional, index to list(value)

        Returns:
        In case of success returns the value, otherwise the original key.
        """
        level = self.config
        if keys and level:
            for key in keys:
                # Check if key is index --> adjust it
                key_to_index = self.get_index_if_is(key)
                # dict
                if isinstance(level, DEEPER_TYPES):
                    if self.check_key_in_level(key, level):
                        level = level[key]
                    else:
                        level = key
                # list
                elif isinstance(level, FLAT_TYPES):
                    # Now we can use index to set/list/forzenset
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
            # Return root list of keys from config else empty
            try:
                return level
            except Exception:
                logger.error(
                    "Problem with geting list of keys from level '%s'",
                    level.keys())
                return None

    def get_config_path(self) -> str | None:
        """Returns path to config file."""
        config_path = None
        if self.config_path:
            config_path = str(Path(self.config_path).absolute())
        return config_path

    def get_specified_type(self, items):
        """Return type or shortcut based on item type.

        Takes value and compares it to list of supported(advanced) types
        which needs to be converted to shortcut format used by UI.
        If not advanced, returns the original value.
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
        """Get(creates) shortcut for value type.

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

    def create_config_deep_path(self, parts) -> str:
        """Creates path to specific level of config file.

        Used for UI. In UI we are using only string type.add()

        Args:
        parts = list of keys

        Returns:
        Path in string format
        """
        return "/".join(parts)

    def go_level_up(self, last_key) -> bool:
        """Decide if last_key is key for move up or not.

        Helps to discover to add key to keychain or not

        Args:
        last_key = last clicked key(treewidget)

        Returns:
        True in case yes
        """
        level_up = False
        if last_key in LEVEL_UP:
            level_up = True
        return level_up

    def let_through(self, key, value) -> bool:
        """Deside if given values are ok to continue or not

        Args:
        key = key column from config treewidget table
        value = value column from config treewidget table

        Return:
        True if ok, otherwise False
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
        """Get struct tags object."""
        return self.config_struct_tags

    def set_config_struct_tags_from_config(self):
        """Get config struct tags from config file."""
        # Tag for more advanced type (dict, list, frozenset, set)
        if self.config:
            self.config_struct_tags["advanced"] = \
                self.get_value_for_key(TAG_ADVANCED)
            self.config_struct_tags["level_up"] = \
                self.get_value_for_key(TAG_LEVEL_UP)

    def is_advanced_type(self, name) -> bool:
        """Check if name is in list of advanced types.

        Params:
        name = name of the type

        Returns:
        True in case it is advanced type, otherwise False
        """
        advanced = False
        if name:
            if name in SUPPORT_ADVANCED:
                advanced = True
        return advanced

    def get_index_if_is(self, key) -> int | None:
        """Check if key is in index form. If is, returns the index.

        Params:
        key = key to check

        Returns:
        If key is in index form return the index, otherwise None.
        """
        if re.search(INDEX_REGEX, key):
            parts = key.split("..")[-1]
            try:
                return int(parts[-1])
            except Exception as e:
                logger.error("Its not valid index in config file %s.", e)
        return None

    def can_i_edit_object_of_type(self, object_type: str) -> bool:
        """Check if I can edit specific type.

        Args:
        object_type = name of the type

        Returns:
        True in case yes, otherwise False
        """
        edit = True
        if object_type and object_type in ADVANCED_TYPE_NAME:
            edit = False
        return edit

    def can_i_apply_changed(
            self, name: str, value, value_type: str, apply_to: str) -> tuple:
        """Can I apply changes based o input, types.

        Args:
        name = name/key
        value = value
        value_type = type(name) of value
        apply_to = can I apply changes to specific type

        Returns:
        can_apply = True in case ok, otherwise False
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
        """Use received chain of keys to search inside config object.

        Find all valid key+value pairs and conver them to format used
        by UI.

        Args:
        level = list of keys in list format, form left to right.
                1. If list is empty --> root level of config file
                2. If not empty --> recursively goes down and return value

        Returns:
        Tuple, it contains list of converted lines(key+value) and
        chain of keys to get to this level inside the config.
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
            # Add current level
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

            # Not root level
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
                            ("|-" + str(_previous_value), str(_previous_value)))
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

                # Insert "level up" tag
                previous.insert(0, ("|-..", ".."))
                _values_out += previous
            else:
                # Show root
                _values_out = []
                root_keys = self.get_value_for_key(None)
                for key in root_keys:
                    value = self.get_value_for_key([key])
                    value_type = self.get_specified_type(value)
                    _values_out += [("|-" + str(key), value if
                                    not value_type else value_type)]
                # Add current level to root overview
                _values_out.insert(0, (".", "."))
        return (_values_out, _valid_level)

    def apply_to_config(
            self,
            keys_chain,
            remove=False,
            edit=None,
            add=None,
            item_index=None) -> bool:
        """Applies required chnages to config object.

        Supports:
        remove = Remove specified item
        edit = alter selected item
        add = add new item to specified position in config object

        Args:
        keys_chain = chain of keys --> to get to level where to apply changes
        remove = simple True or False
        edit = tuple with (key, value) to alter
        add = typle with (key, value) to add
        item_index = optional index in case changes are applied over list
                     (index in list)

        Returns:
        True in case everything ok, otherwise False
        """
        applied = True
        try:
            # We have chain of keys and config to be altered
            if keys_chain and self.config:
                # To store level where to apply and key at that level
                apply_object, apply_object_key = None, None
                # Start searching root level
                working_list = [self.config]
                while working_list:
                    # Start from forst key
                    for watch_key in keys_chain:
                        # Is this key index? Format '..1',
                        index = self.get_index_if_is(watch_key)
                        # Get item from list of search items
                        current_item = working_list.pop()
                        if isinstance(current_item,
                                      FLAT_TYPES):
                            # List
                            keys_match = [match_key for match_key
                                          in current_item
                                          if match_key == watch_key]
                            # Match to out key
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
                                # No match, try index(from lchain of keys)
                                index_value = current_item[index]
                                apply_object_key = index
                                apply_object = current_item
                                working_list.append(index_value)
                            elif item_index is not None \
                                    and len(current_item) >= item_index:
                                # No match, not valid index, try item_index
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
                                # Go through it
                                for key_current, value_current in \
                                        current_item.items():
                                    # Match on key, store final
                                    # level+key and add it to search list.
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
                    # Here apply changes
                    if remove:
                        # Remove
                        try:
                            del apply_object[apply_object_key]
                        except Exception as e:
                            logger.error(
                                "Problem with remove something from config\
                                object/structure(%s).", e)
                            applied = False
                    elif edit is not None:
                        # Strip - key and value - remove empty trailing chars
                        edit_key = edit[0].strip()
                        # Check if can strip it, if not keep the original
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
                                        # Key is different
                                        del apply_object[apply_object_key]

                                        apply_object[edit_key] = edit_value
                                    elif apply_object_key == edit[0]:
                                        # Key is same, just replace the value
                                        apply_object[edit_key] = edit_value
                                else:
                                    # apply_object[apply_object_key] = edit[1]
                                    apply_object[apply_object_key] = edit_value
                            except Exception as e:
                                logger.error(
                                    "Problem with editing something in config\
                                    object/structure(%s).", e)
                                applied = False
                        else:
                            logger.error(
                                """Cannot edit item to config.
                                Some attributs are missing '%s'""", add)
                            applied = False
                    elif add is not None:
                        # Strip - key and value - remove empty trailing chars
                        add_key = add[0].strip()
                        # Check if can strip it, if not keep the original
                        add_value = add[1]
                        if isinstance(add[1], STR_TYPE):
                            add_value = add[1].strip()
                        # Add new item
                        if None not in add:
                            # Add items
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
                                        "Cannot add item '%s' to config file, \
                                        unknown type.", add)
                                    applied = False
                            except Exception as e:
                                logger.error(
                                    "Problem with add something to config\
                                    object/structure(%s).", e)
                                applied = False
                        else:
                            logger.error(
                                """Cannot add item to config.
                                Some attributs are missing '%s'""", add)
                            applied = False

            elif not keys_chain and self.config:
                # Root level
                if add:
                    add_key = add[0].strip()
                    # Check if can strip it, if not keep the original
                    add_value = add[1]
                    if isinstance(add[1], STR_TYPE):
                        add_value = add[1].strip()
                    # Only add possible
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
                "Trying to apply changes to config file failed(%s).", e)
            applied = False
        return applied
