# -*- coding: utf-8 -*-
"""Test covering config logic."""

import json
from pathlib import Path


def test_get_config_object(config_logic_instance_default_config_file):
    """Try to get the config object."""
    config = config_logic_instance_default_config_file.get_config_object()
    assert config is not None
    assert isinstance(config, dict)


def test_load_config(tmp_path, config_logic_instance_default_config_file):
    """It expects a new config file(file_path) and reads its
    content, storing it in the config object.
    """
    # Prepare a new simple config file
    new_config = Path(tmp_path).joinpath("new_config.json")
    # Fill the new config
    new_config_content = {"key": "value"}
    with open(new_config, "w", encoding='utf-8') as file_out:
        file_out.write(json.dumps(new_config_content, indent=4))
    # Call reload
    config_logic_instance_default_config_file.load_config(
        config_file_name=new_config)
    # Get the config content
    config = config_logic_instance_default_config_file.get_config_object()
    assert config == new_config_content


def test_save_config(tmp_path, config_logic_instance_default_config_file):
    """Save config to file."""
    # Prepare a new simple config file
    new_config = Path(tmp_path).joinpath("new_config.json")
    # Just create it --> can be used for storage
    with open(new_config, "w", encoding='utf-8') as _:
        pass
    config_logic_instance_default_config_file.save_config(
        new_config)
    assert new_config.exists()
    # Get the new config content
    new_content = None
    with open(new_config, "r", encoding='utf-8') as file_out:
        new_content = json.loads(file_out.read())
    assert new_content is not None
    # Get the current config object
    current_config = config_logic_instance_default_config_file.\
        get_config_object()
    assert current_config is not None
    assert current_config == new_content


def test_apply_to_config_add_valid(config_logic_instance_default_config_file):
    """Try to add something to the config file.

    Attemps to add a valid item to the config object.
    """
    # Add item to "help" --> add key="test", value=0
    keys_chain = ["help"]
    add_pair = ("test", 0)
    applied = config_logic_instance_default_config_file.apply_to_config(
        keys_chain,
        add=add_pair
    )
    assert applied
    # Get the config object
    config = config_logic_instance_default_config_file.get_config_object()
    part = config_logic_instance_default_config_file.get_value_for_key(
        keys_chain)
    assert config is not None
    assert part is not None
    assert add_pair[0] in part
    assert part[add_pair[0]] == add_pair[1]


def test_apply_to_config_edit_valid(config_logic_instance_default_config_file):
    """Try to edit something in the config file.

    Attemps to edit a valid item in the config object.
    """
    keys_chain = ["max_resolution", "X"]
    # Prepare a new key-value pair
    edit_pair = ("X", 1234)
    applied = config_logic_instance_default_config_file.apply_to_config(
        keys_chain,
        edit=edit_pair
    )
    assert applied
    # Get the config object
    config = config_logic_instance_default_config_file.get_config_object()
    part = config_logic_instance_default_config_file.get_value_for_key(
        keys_chain)
    assert config is not None
    assert part is not None
    assert part == edit_pair[1]


def test_apply_to_config_remove_valid(
        config_logic_instance_default_config_file):
    """Try to remove something from config file.

    Tries to remove a valid item from teh config object.
    """
    # What to remove
    keys_chain = ["max_resolution"]
    applied = config_logic_instance_default_config_file.apply_to_config(
        keys_chain,
        remove=True
    )
    assert applied
    # Get the config object
    config = config_logic_instance_default_config_file.get_config_object()
    part = config_logic_instance_default_config_file.get_value_for_key(
        keys_chain)
    assert config is not None
    assert part == keys_chain[0]


def test_apply_to_config_remove_not_valid(
        config_logic_instance_default_config_file):
    """Try to remove something from the config file.

    Tries to remove a valid item from the config object.
    """
    # Key chain
    keys_chain = ["abc", "def"]
    # Before remove
    config_before = config_logic_instance_default_config_file.\
        get_config_object()
    # Remove it
    applied = config_logic_instance_default_config_file.apply_to_config(
        keys_chain,
        remove=True
    )
    assert applied is False
    config_after = config_logic_instance_default_config_file.\
        get_config_object()
    assert config_before == config_after


def test_set_config_object_to_none(config_logic_instance_default_config_file):
    """Try to set the config object to None.

    It should preserve the original config object.
    The new object should be of the same type as the original(dict).
    """
    current = config_logic_instance_default_config_file.get_config_object()
    # Set the new object
    config_logic_instance_default_config_file.set_config_object(None)
    new = config_logic_instance_default_config_file.get_config_object()
    assert current == new


def test_set_config_object_to_new(config_logic_instance_default_config_file):
    """Try to set the config object to None.

    It should replace the config object.
    """
    # Set the new object
    new_config = {"is": "new"}
    config_logic_instance_default_config_file.set_config_object(new_config)
    new = config_logic_instance_default_config_file.get_config_object()
    assert new_config == new


def test_check_key_in_level_existing(
        config_logic_instance_default_config_file):
    """Check if a key exists in the current level(in dict).

    Returns True or False.
    """
    key = "name"
    level = config_logic_instance_default_config_file.get_config_object()
    exists = config_logic_instance_default_config_file.\
        check_key_in_level(key, level)
    assert exists


def test_check_key_in_level_not_existing(
        config_logic_instance_default_config_file):
    """Check if a key exists in the current level(in dict).

    Returns True or False.
    """
    key = "abracadabra"
    level = config_logic_instance_default_config_file.get_config_object()
    exists = config_logic_instance_default_config_file.\
        check_key_in_level(key, level)
    assert exists is False


def test_get_value_for_key_existing(config_logic_instance_default_config_file):
    """Get the value for a key.

    Test an existing key.
    """
    keys = ["max_resolution", "X"]
    value = config_logic_instance_default_config_file.get_value_for_key(keys)
    assert value is not None


def test_get_value_for_key_not_existing(
        config_logic_instance_default_config_file):
    """Get the value for a key.

    Test a not_existing key. It should return the original value.
    """
    keys = ["max_resolution", "ukulele"]
    value = config_logic_instance_default_config_file.get_value_for_key(keys)
    assert value == "ukulele"


def test_get_value_for_key_recursive_existing(
        config_logic_instance_default_config_file):
    """Get the value for a key.

    Test an existing key.
    """
    keys = ["max_resolution", "X"]
    value = config_logic_instance_default_config_file.get_value_for_key(keys)
    assert value is not None


def test_get_value_for_key_recursive_not_existing(
        config_logic_instance_default_config_file):
    """Get the value for a key.

    Testing a not_existing key. It should return the original value.
    """
    keys = ["max_resolution", "ukulele"]
    value = config_logic_instance_default_config_file.get_value_for_key(keys)
    assert value == "ukulele"


def test_can_i_edit_object_type_valid(
        config_logic_instance_default_config_file):
    """Check if the type can be edited.

    Expects name as a string e.g. 'dict', 'abc'.
    Returns True or False.
    """
    type_name = "number"
    edit = config_logic_instance_default_config_file.\
        can_i_edit_object_of_type(type_name)
    assert edit


def test_can_i_edit_object_type_not_valid(
        config_logic_instance_default_config_file):
    """Check if the type can be edited.

    Expects name as a string e.g. 'dict', 'abc'.
    Returns True, False.
    """
    type_name = "dict"
    edit = config_logic_instance_default_config_file.\
        can_i_edit_object_of_type(type_name)
    assert edit is False


def test_can_i_apply_changes_possible_str(
        config_logic_instance_default_config_file):
    """Check if changes can be applied to the current item.

    For example:
    name='name'
    value='value'
    value_type='string'
    apply_to = 'string'
    ==> Allowed

    name='name'
    value='1'
    value_type='number'
    apply_to = 'string'
    ==> Not allowed
    """
    name = "name"
    value = "value"
    value_type = "string"
    apply_to = "string"
    can_apply, name_msg, value_msg, type_msg = \
        config_logic_instance_default_config_file.can_i_apply_changed(
            name, value, value_type, apply_to)
    assert can_apply
    assert not name_msg
    assert not value_msg
    assert not type_msg


def test_can_i_apply_changes_possible_dict(
        config_logic_instance_default_config_file):
    """Check if changes can be applied to the current item.

    For example:
    name='name'
    value='value'
    value_type='string'
    apply_to = 'string'
    ==> Allowed

    name='name'
    value='1'
    value_type='number'
    apply_to = 'string'
    ==> Not allowed
    """
    name = "name"
    value = "value"
    value_type = "dict"
    apply_to = "string"
    can_apply, name_msg, value_msg, type_msg =\
        config_logic_instance_default_config_file.can_i_apply_changed(
            name, value, value_type, apply_to)
    assert can_apply
    assert not name_msg
    assert not value_msg
    assert not type_msg


def test_can_i_apply_changes_not_possible_number(
        config_logic_instance_default_config_file):
    """Check if changes can be applied to the current item.

    For example.
    name='name'
    value='value'
    value_type='string'
    apply_to = 'string'
    ==> Allowed

    name='name'
    value='1'
    value_type='number'
    apply_to = 'string'
    ==> Not allowed
    """
    name = ""
    value = "1"
    value_type = "number"
    apply_to = "dict"
    can_apply, name_msg, value_msg, type_msg =\
        config_logic_instance_default_config_file.can_i_apply_changed(
            name, value, value_type, apply_to)
    assert not can_apply
    assert name_msg
    assert not value_msg
    assert not type_msg


def test_get_list_of_keys_root_level(
        config_logic_instance_default_config_file):
    """Get a list of keys from the root level."""
    keys_chain = []
    values_out, valid_level = config_logic_instance_default_config_file.\
        get_list_of_keys(keys_chain)
    assert values_out is not None
    assert valid_level == []


def test_get_list_of_keys_not_existing(
        config_logic_instance_default_config_file):
    """Get a list of keys from the root level."""
    keys_chain = ["abc"]
    values_out, valid_level = config_logic_instance_default_config_file.\
        get_list_of_keys(keys_chain)
    # Always "|..", ".." at least + original value
    assert values_out is not None
    assert values_out is not None


def test_get_name_for_type_known(config_logic_instance_default_config_file):
    """Get the name for a type(python type converted) used by the UI."""
    # Supported
    type_name = "str"
    expected_name = "string"
    name = config_logic_instance_default_config_file.get_name_for_type(
        type_name)
    assert name == expected_name


def test_get_name_for_type_unknown(config_logic_instance_default_config_file):
    """Get the name for a type(python type converted) used by the UI."""
    # Unsupported
    type_name = True
    expected_name = "string"
    name = config_logic_instance_default_config_file.get_name_for_type(
        type_name)
    assert name == expected_name


def test_get_list_of_type_names(config_logic_instance_default_config_file):
    """Get a list of supported types (strings) used by the UI."""
    supported = config_logic_instance_default_config_file.\
        get_list_of_type_names()
    assert supported is not None
    assert isinstance(supported, list)


def test_get_resolution(config_logic_instance_default_config_file):
    """Get the resolution from the default config file."""
    resolution = config_logic_instance_default_config_file.get_resolution()
    assert resolution is not None
    assert isinstance(resolution, tuple)


def test_get_title(config_logic_instance_default_config_file):
    """Get the title from the config file."""
    title = config_logic_instance_default_config_file.get_title()
    assert title is not None
    assert isinstance(title, str)


def test_get_name(config_logic_instance_default_config_file):
    """Get the name from the config file."""
    name = config_logic_instance_default_config_file.get_name()
    assert name is not None
    assert isinstance(name, str)


def test_get_version(config_logic_instance_default_config_file):
    """Get the version from the config file."""
    version = config_logic_instance_default_config_file.get_version()
    assert version is not None
    assert isinstance(version, str)


def test_get_contact(config_logic_instance_default_config_file):
    """Get the contact from the config file."""
    contact = config_logic_instance_default_config_file.get_contact()
    assert contact is not None
    assert isinstance(contact, str)


def test_get_homepage(config_logic_instance_default_config_file):
    """Get the homepage from the config file."""
    homepage = config_logic_instance_default_config_file.get_homepage()
    assert homepage is not None
    assert isinstance(homepage, str)


def test_get_description(config_logic_instance_default_config_file):
    """Get the description from the config file."""
    desc = config_logic_instance_default_config_file.get_description()
    assert desc is not None
    assert isinstance(desc, str)


def test_get_value_type_help_supported(
        config_logic_instance_default_config_file):
    """Get the help message for a specific type.

    Supported type.
    """
    type_name = "string"
    help_msg = config_logic_instance_default_config_file.\
        get_value_type_help(type_name)
    assert help_msg is not None
    assert isinstance(help_msg, str)


def test_get_value_type_help_unsupported(
        config_logic_instance_default_config_file):
    """Get the help message for a specific type.

    Unsupported type.
    """
    type_name = "bool"
    help_msg = config_logic_instance_default_config_file.\
        get_value_type_help(type_name)
    assert help_msg is None


def test_convert_value_to_type_dict(config_logic_instance_default_config_file):
    """Convert a type value/name to its actual value(based on the given value).

    Only supported types are allowed. Otherwise, original value is returned.

    For example.
    value = "==>dict"
    value_type = dict

    value = "1"
    value_type = number
    """
    value = "==>dict"
    value_type = "dict"
    expected_value = {}
    new_value = config_logic_instance_default_config_file.\
        convert_value_to_type(value_type, value)
    assert new_value == expected_value


def test_convert_value_to_type_number(
        config_logic_instance_default_config_file):
    """Convert a type value/name to its actual value(based on the given value).

    Only supported types are allowed. Otherwise, original value is returned.

    For example.
    value = "==>dict"
    value_type = dict

    value = "1"
    value_type = number
    """
    value = "1"
    value_type = "number"
    expected_value = 1
    new_value = config_logic_instance_default_config_file.\
        convert_value_to_type(value_type, value)
    assert new_value == expected_value


def test_convert_value_to_type_unknown_type(
        config_logic_instance_default_config_file):
    """Convert a type value/name to its actual value(based on the given value).

    Only supported types are allowed. Otherwise, original value is returned.

    For example.
    value = "==>dict"
    value_type = dict

    value = "1"
    value_type = number
    """
    value = "True"
    value_type = "bool"
    new_value = config_logic_instance_default_config_file.\
        convert_value_to_type(value_type, value)
    assert new_value == value


def test_get_config_path(config_logic_instance_default_config_file):
    """Test to geting the path to the config file."""
    config_path = config_logic_instance_default_config_file.get_config_path()
    assert config_path is not None
    assert Path(config_path).exists()


def test_get_specified_type_simple_advanced(
        config_logic_instance_default_config_file):
    """Test if a given value is an advanced type or not.

    If it is an advanced type, it returns the shortcut, otherwise its
    returns the original value.
    Uses the method 'get_type_of_value_shortcut'.
    """
    # Simple
    simple_value = "abc"
    short = config_logic_instance_default_config_file.\
        get_specified_type(simple_value)
    assert short is not None
    assert short == short
    # Advanced
    advanced_type = {"is": "advanced"}
    short_result = "==>dict"
    short = config_logic_instance_default_config_file.\
        get_specified_type(advanced_type)
    assert short is not None
    assert short == short_result


def test_get_type_of_value_shortcut(
        config_logic_instance_default_config_file):
    """Get the shortcut for a specific type of value.

    Takes a value and compares it to the list of supported (advanced) types,
    converting it to the shortcut format used by the UI.
    If the value is not advanced, returns None.
    """
    # Advanced types
    advanced_types_list = (list, dict)
    # Valid
    simple_value = "abc"
    short_simple = config_logic_instance_default_config_file.\
        get_type_of_value_shortcut(simple_value, advanced_types_list)
    assert short_simple is None
    # Advanced
    advanced = {"is": "advanced"}
    short = "==>dict"
    short_advanced = config_logic_instance_default_config_file.\
        get_type_of_value_shortcut(advanced, advanced_types_list)
    assert short_advanced == short


def test_create_config_deep_path_valied(
        config_logic_instance_default_config_file):
    """Create a 'deep' path for the UI. Expects a list of string.

    This method is called from the config widget, where we work only with
    strings (displayed in the UI).
    """
    parts = ["a", "..0", "b", "..1"]
    created_path = "a/..0/b/..1"
    path = config_logic_instance_default_config_file.\
        create_config_deep_path(parts)
    assert path is not None
    assert path == created_path


def test_go_level_up_valid(config_logic_instance_default_config_file):
    """Determine whether to add a key to the chain of keys.

    Valid 'level up' values are '.' '..'
    """
    key_1 = "."
    valid = config_logic_instance_default_config_file.go_level_up(key_1)
    assert valid
    key_2 = ".."
    valid = config_logic_instance_default_config_file.go_level_up(key_2)
    assert valid


def test_go_level_up_not_valid(config_logic_instance_default_config_file):
    """Determine whether to add a key to the chain of keys.

    Valid "level up" values are '.' '..'
    """
    key_1 = 1
    valid = config_logic_instance_default_config_file.go_level_up(key_1)
    assert valid is False
    key_2 = "1"
    valid = config_logic_instance_default_config_file.go_level_up(key_2)
    assert valid is False


def test_let_through_valid_level_up(config_logic_instance_default_config_file):
    """Test if the current key and value are valid to continue.

    For navigating "up" or "down".
    """
    # Level up
    key = ".."
    value = ".."
    valid_up = config_logic_instance_default_config_file.let_through(
        key, value
    )
    assert valid_up


def test_let_through_valid_level_down(
        config_logic_instance_default_config_file):
    """Test if the current key and value are valid to continue.

    For navigating "up" or "down".
    """
    # Level up
    key = "."
    value = "==>dict"
    valid_down = config_logic_instance_default_config_file.let_through(
        key, value
    )
    assert valid_down


def test_get_config_struct_tags_from_config(
        config_logic_instance_default_config_file):
    """Get struct tags from the config file.

    Targets the "level up", "advanced" tags
    """
    config_logic_instance_default_config_file.\
        set_config_struct_tags_from_config()
    tags = config_logic_instance_default_config_file.\
        get_config_struct_tags_dict()
    assert tags is not None
    assert isinstance(tags, dict)


def test_is_advanced_type_valid(config_logic_instance_default_config_file):
    """Test if a type name (UI) is an advanced type or not.

    Advanced types are listed at the top of the file 'config_logic.py'.
    """
    valid = "==>dict"
    is_valid = config_logic_instance_default_config_file.\
        is_advanced_type(valid)
    assert is_valid


def test_is_advanced_type_not_valid(config_logic_instance_default_config_file):
    """Test if a type name (UI) is an advanced type or not.

    Advanced types are listed at the top of the file 'config_logic.py'.
    """
    not_valid = "abc"
    is_valid = config_logic_instance_default_config_file.\
        is_advanced_type(not_valid)
    assert is_valid is False


def test_get_index_if_is_valid(config_logic_instance_default_config_file):
    """Test if a string is an index or not.

    Validates the index and returns it if valid.
    """
    value = "..1"
    valid_index = 1
    it_is = config_logic_instance_default_config_file.get_index_if_is(value)
    assert it_is == valid_index


def test_get_index_if_is_not_valid(config_logic_instance_default_config_file):
    """Test if a string is an index or not.

    Validates the index and returns it if valid.
    """
    value = "abc"
    not_valid_index = None
    it_is = config_logic_instance_default_config_file.get_index_if_is(value)
    assert it_is is not_valid_index


def test_get_index_if_is_partly_valid(
        config_logic_instance_default_config_file):
    """Test if a string is an index or not.

    Tests an invalid index. A valid index should look like '..1' (dot-dot-int).
    """
    value = "...abc"
    not_valid_index = None
    it_is = config_logic_instance_default_config_file.get_index_if_is(value)
    assert it_is is not_valid_index
