# -*- coding: utf-8 -*-
"""Update logic tests."""

import shutil
from cvyt.update.update_logic import UpdateLogic
from cvyt.default_app_config import DEFAULT_CONFIG
from pathlib import Path


def test_init_update_folder_apply_on_via_constructor(
        create_modules_archive,
        config_logic_instance_default_config_file,
        tmp_path,
        get_dummy_module_name):
    """Init update.

    Path to the folder where the update will be applied is passed
    via the constructor.
    """
    # Archive path
    archive_path = create_modules_archive
    assert archive_path.exists()
    # Ne config -> alter the root folder for modules
    DEFAULT_CONFIG["modules"]["root"] = str(tmp_path)
    # Set new config object
    config_logic_instance_default_config_file.set_config_object(DEFAULT_CONFIG)
    # Update logic
    logic = UpdateLogic(
        config=config_logic_instance_default_config_file,
        temp_update=str(tmp_path)
    )
    logic.process_archive(str(archive_path))
    # List of files, folders before update
    before_update = [item for item in Path(tmp_path).iterdir()]
    assert before_update
    # Flag to signal uthe pdate finished - successfully
    applied = True
    for status, msg in logic.initiate_update():
        if not status:
            applied = False
    # Update applied successfully
    assert applied is True
    # Check changes(updates) after update is applied
    after_update = [item for item in tmp_path.iterdir()]
    assert before_update != after_update
    # Check if the new folder(updated module) is present
    updated_exists = False
    for module in after_update:
        if module.name == get_dummy_module_name:
            updated_exists = True
            break
    assert updated_exists

    # Clean
    if Path(tmp_path).exists():
        shutil.rmtree(tmp_path, ignore_errors=True)
    del logic


def test_init_update_folder_apply_on_via_method_arg(
        create_modules_archive,
        config_logic_instance_default_config_file,
        tmp_path,
        get_dummy_module_name):
    """Init update.

    The path to the folder where the update will be applied is passed
    via arg.
    """
    # Archive path
    archive_path = create_modules_archive
    assert archive_path.exists()
    # Ne config -> alter the root folder for modules
    DEFAULT_CONFIG["modules"]["root"] = str(tmp_path)
    # Set the new config object
    config_logic_instance_default_config_file.set_config_object(DEFAULT_CONFIG)
    # Update logic
    logic = UpdateLogic(
        config=config_logic_instance_default_config_file
    )
    logic.process_archive(str(archive_path), str(tmp_path))
    # List of files, folders before update
    before_update = [item for item in Path(tmp_path).iterdir()]
    assert before_update
    # Flag to signal that the update finished - successfully
    applied = True
    for status, msg in logic.initiate_update():
        if not status:
            applied = False
    # Update applied successfully
    assert applied is True
    # Check changes(updates) after the update is applied
    after_update = [item for item in tmp_path.iterdir()]
    assert before_update != after_update
    # Check if the new folder(updated module) is present
    updated_exists = False
    for module in after_update:
        if module.name == get_dummy_module_name:
            updated_exists = True
            break
    assert updated_exists

    # Clean
    if Path(tmp_path).exists():
        shutil.rmtree(tmp_path, ignore_errors=True)
    del logic


def test_process_modules_archive_available_modules(
        create_modules_archive,
        create_update_logic,
        tmp_path):
    """Try to decompress the modules archive.

    Check:
    - available modules == 1
    """
    archive_path = create_modules_archive
    assert archive_path.exists()
    # Process the archive
    create_update_logic.process_archive(str(archive_path), tmp_path)
    # Get available modules
    modules = create_update_logic.get_available_modules()
    # Modules found
    assert modules is not None
    module_counter = 0
    for name, module in modules:
        assert name
        assert module
        module_counter += 1
    # Expecting a module
    assert module_counter == 1


def test_get_description_for_module(
        create_update_logic,
        create_modules_archive,
        tmp_path):
    archive_path = create_modules_archive
    assert archive_path.exists()
    # Process the archive
    create_update_logic.process_archive(archive_path, tmp_path)
    # Get available modules
    modules = create_update_logic.get_available_modules()
    # Modules found
    assert modules is not None
    for name, module in modules:
        assert name
        assert module
        # Get the description
        desc = module.get("description", None)
        assert desc
        assert isinstance(desc, str)
    # Clean
    if Path(tmp_path).exists():
        shutil.rmtree(tmp_path, ignore_errors=True)


def test_set_update_status(
        create_update_logic,
        create_modules_archive,
        tmp_path):
    archive_path = create_modules_archive
    assert archive_path.exists()
    # Process the archive
    create_update_logic.process_archive(archive_path, tmp_path)
    # Get available modules
    modules = create_update_logic.get_available_modules()
    # Modules found
    assert modules is not None
    # Module name to set the new status to
    module_name = None
    previous_status = None
    for name, module in modules:
        assert name
        assert module
        module_name = name
        previous_status = module.get("update", None)
    assert previous_status is not None
    # Set the status
    create_update_logic.set_module_update_status(
        module_name, not previous_status)
    # Check the status again
    modules = create_update_logic.get_available_modules()
    for name, module in modules:
        if name == module_name:
            assert module.get("update") != previous_status
    # Clean
    if Path(tmp_path).exists():
        shutil.rmtree(tmp_path, ignore_errors=True)


def test_remove_archive(
        create_update_logic,
        create_modules_archive):
    """Try to remove the archive."""
    archive_path = create_modules_archive
    # Check if the archive exists
    assert archive_path.exists()
    # Remove the archive
    create_update_logic.remove_archive(archive_path)
    # Check if the archive exists
    assert not archive_path.exists()
