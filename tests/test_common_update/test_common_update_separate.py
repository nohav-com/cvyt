# -*- coding: utf-8 -*-
"""Common update tests."""

from pathlib import Path


def test_get_available_modules(
        common_update_instance_ok,
        create_dummy_module):
    """Get available modules."""
    path, _ = create_dummy_module
    common_update_instance_ok.create_update_list(path)
    module_counter = 0
    for name, module in common_update_instance_ok.get_available_modules():
        if name and module:
            module_counter += 1
    assert module_counter > 0


def test_get_count_available_modules_valid(
        common_update_instance_ok,
        create_dummy_module
):
    """Get count of available module."""
    path, _ = create_dummy_module
    common_update_instance_ok.create_update_list(path)
    module_counter = common_update_instance_ok.get_count_of_available_modules()
    assert module_counter > 0


def test_get_count_available_modules_not_valid(common_update_instance_ok):
    """Get count of available modules when no modules are present."""
    module_counter = common_update_instance_ok.get_count_of_available_modules()
    assert module_counter == 0


def test_get_value_for_key_existing_module(
    create_dummy_module,
    common_update_instance_ok,
    get_dummy_module_name
):
    """Set value for a key in a existing module."""
    key = "description"
    path, _ = create_dummy_module
    common_update_instance_ok.create_update_list(path)
    value = common_update_instance_ok.get_value_for_key(
        get_dummy_module_name, key)
    assert value


def test_get_value_for_key_not_existing_module(
    create_dummy_module,
    common_update_instance_ok,
    get_dummy_module_name
):
    """Set value for key in a not-existing module."""
    key = "description"
    path, _ = create_dummy_module
    common_update_instance_ok.create_update_list(path)
    value = common_update_instance_ok.get_value_for_key(
        "abracadabra", key)
    assert not value


def test_set_value_for_key_existing_key_existing_module(
        create_dummy_module,
        common_update_instance_ok,
        get_dummy_module_name
):
    """Alter value for an existing key, in an existing module."""
    key = "description"
    altered_value = "altered value"
    path, _ = create_dummy_module
    common_update_instance_ok.create_update_list(path)
    common_update_instance_ok.set_value_for_key(
        get_dummy_module_name,
        key,
        altered_value
    )
    # Get value to check
    value = common_update_instance_ok.get_value_for_key(
        get_dummy_module_name, key)
    assert altered_value == value


def test_get_modules_root_path(common_update_instance_ok):
    """Get path to the root folder of modules."""
    root = common_update_instance_ok.get_modules_root_path()
    assert root


def test_get_module_existing(
        create_dummy_module,
        common_update_instance_ok,
        get_dummy_module_name
):
    """Get module info for an existing one."""
    path, _ = create_dummy_module
    common_update_instance_ok.create_update_list(path)
    module = common_update_instance_ok.get_module(get_dummy_module_name)
    assert module


def test_get_module_not_existing(
        common_update_instance_ok,
        get_dummy_module_name
):
    """Get module info for not-existing module."""
    module = common_update_instance_ok.get_module(get_dummy_module_name)
    assert not module


def test_get_required_files(
        common_update_instance_ok,
        get_required_chain_of_keys
):
    """Get list of required files/folder for a module."""
    required = common_update_instance_ok.get_required_files(
        get_required_chain_of_keys)
    assert required


def test_create_update_list_existing(
        create_dummy_module,
        common_update_instance_ok
):
    """Create update list of modules from an existing modules folder."""
    path, _ = create_dummy_module
    common_update_instance_ok.create_update_list(path)
    module_counter = 0
    for name, module in common_update_instance_ok.get_available_modules():
        if name and module:
            module_counter += 1
    assert module_counter > 0


def test_create_update_list_not_existing(common_update_instance_ok):
    """Create update list of modules from a not-existing folder."""
    common_update_instance_ok.create_update_list("abracadabra")
    module_counter = 0
    for name, module in common_update_instance_ok.get_available_modules():
        if name and module:
            module_counter += 1
    assert module_counter == 0


def test_create_update_list_empty(common_update_instance_ok):
    """Create update list of modules from an empty folder."""
    common_update_instance_ok.create_update_list(str(Path(__file__).parent))
    module_counter = 0
    for name, module in common_update_instance_ok.get_available_modules():
        if name and module:
            module_counter += 1
    assert module_counter == 0


def test_get_only_folders_from_root_folder_existing(
        create_dummy_module,
        common_update_instance_ok
):
    """Get root folders from an existing folder."""
    path, _ = create_dummy_module
    folders = common_update_instance_ok.get_only_folders_from_root_folder(
        str(path))
    assert folders


def test_get_only_folders_from_root_folder_not_existing(
        common_update_instance_ok
):
    """Get root folders from a not-existing folder."""
    folders = common_update_instance_ok.get_only_folders_from_root_folder(
        "abracadabra")
    assert not folders


def test_get_only_folders_from_root_folder_empty(
        common_update_instance_ok,
        tmp_path
):
    """Get root folders from an empty folder."""
    folders = common_update_instance_ok.get_only_folders_from_root_folder(
        tmp_path)
    assert not folders


def test_get_detailed_info_about_module_existing(
        create_dummy_module,
        common_update_instance_ok,
        get_dummy_module_name
):
    """Get detailed info about an existing module."""
    path, _ = create_dummy_module
    common_update_instance_ok.create_update_list(path)
    detailed = common_update_instance_ok.get_detailed_info_about_module(
        get_dummy_module_name
    )
    assert detailed


def test_get_detailed_info_about_module_not_existing(
        create_dummy_module,
        common_update_instance_ok
):
    """Get detailed info about a not-existing module."""
    path, _ = create_dummy_module
    common_update_instance_ok.create_update_list(path)
    detailed = common_update_instance_ok.get_detailed_info_about_module(
        "abracadabra"
    )
    assert not detailed


def test_check_valid_content_of_module_not_existing(
        common_update_instance_ok,
        get_required_chain_of_keys
):
    """Check valid content of a module(folder)."""
    valid = common_update_instance_ok.check_valid_content(
        Path(__file__),
        get_required_chain_of_keys)
    assert not valid


def test_add_rest_of_required_info_about_module_existing(
        create_dummy_module,
        common_update_instance_ok,
        get_dummy_module_name
):
    """Add the rest of the required info for an existing module."""
    altered_key = "description"
    path, _ = create_dummy_module
    common_update_instance_ok.create_update_list(path)
    # Remove the rest of the required info(1 item)
    common_update_instance_ok.set_value_for_key(
        get_dummy_module_name,
        altered_key,
        ""
    )
    # Check if it's altered
    for name, module in common_update_instance_ok.get_available_modules():
        assert name
        assert module
        # Check if the key is altered
        assert not module.get(altered_key)
    # Add the info again
    common_update_instance_ok.add_rest_of_required_info(get_dummy_module_name)
    # Check if it's altered "back"
    for name, module in common_update_instance_ok.get_available_modules():
        assert name
        assert module
        # Check if the key is altered
        assert module.get(altered_key)


def test_add_rest_of_required_info_about_module_not_existing(
        create_dummy_module,
        common_update_instance_ok
):
    """Add the rest of the required info for a not-existing module."""
    path, _ = create_dummy_module
    common_update_instance_ok.create_update_list(path)
    # Get the names of existing modules
    existing = [name for name, _ in
                common_update_instance_ok.get_available_modules()]
    # Add the info - not existing module
    common_update_instance_ok.add_rest_of_required_info("bracadabra")
    after_existing = [name for name, _ in
                      common_update_instance_ok.get_available_modules()]
    assert existing == after_existing


def test_process_basic_info_about_module_existing(
        create_dummy_module,
        common_update_instance_ok,
        get_dummy_module_name
):
    """Add basic info about an existing module."""
    altered_key = "description"
    path, _ = create_dummy_module
    common_update_instance_ok.create_update_list(path)
    # Remove the rest of the required info(1 item)
    common_update_instance_ok.set_value_for_key(
        get_dummy_module_name,
        altered_key,
        ""
    )
    # Check if it's altered
    for name, module in common_update_instance_ok.get_available_modules():
        assert name
        assert module
        # Check if the key is altered
        assert not module.get(altered_key)
    # Add the info again
    common_update_instance_ok.process_basic_info(get_dummy_module_name)
    # Check if it's altered "back"
    for name, module in common_update_instance_ok.get_available_modules():
        assert name
        assert module
        # Check if the key is altered
        assert module.get(altered_key)


def test_process_basic_info_about_module_not_existing(
        create_dummy_module,
        common_update_instance_ok
):
    """Add basic info for a not-existing module."""
    path, _ = create_dummy_module
    common_update_instance_ok.create_update_list(path)
    # Get the names of existing modules
    existing = [name for name, _ in
                common_update_instance_ok.get_available_modules()]
    # Add info - not existing module
    common_update_instance_ok.process_basic_info("bracadabra")
    after_existing = [name for name, _ in
                      common_update_instance_ok.get_available_modules()]
    assert existing == after_existing


def test_get_module_root_keys_chain(common_update_instance_ok):
    """Get the chain of keys for the modules root folder name."""
    root = common_update_instance_ok.get_modules_root_keys_chain()
    assert root is not None
    assert isinstance(root, list)


def test_get_modules_config_file_name_keys_chain(common_update_instance_ok):
    """Get the chain of keys for the module config file path."""
    config_file = common_update_instance_ok.\
        get_modules_config_file_name_keys_chain()
    assert config_file is not None
    assert isinstance(config_file, list)


def test_get_temp_folder_name(common_update_instance_ok):
    """Get the name for the temp folder."""
    temp_folder = common_update_instance_ok.get_temp_folder_name()
    assert temp_folder is not None
    assert isinstance(temp_folder, str)


def test_get_required_module_content_keys_chain(common_update_instance_ok):
    """Get the chain of keys for the required module content."""
    required = common_update_instance_ok.\
        get_required_module_content_keys_chain()
    assert required is not None
    assert isinstance(required, list)
    assert len(required) > 0
