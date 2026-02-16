import sys


def test_import_dummy_module_correct(
        cvyt_logic_instance_ok,
        create_dummy_module,
        get_dummy_module_name):
    """Try to import dummy_module."""
    # Get dummy module name
    dummy_module_name = get_dummy_module_name
    # Get temp folder for modules, available modules model
    temp_module, available_modules = create_dummy_module
    assert temp_module.exists()
    # Create list of available modules
    available_modules.create_modules_list()
    dummy_module_info = available_modules.get_module_info(dummy_module_name)
    assert dummy_module_info
    # Import module
    module = cvyt_logic_instance_ok.import_module(
        dummy_module_name, dummy_module_info, "Dummy notning", "dummy_nothing"
    )
    assert module


def test_cvyt_logic_remove_not_existing_key(cvyt_logic_instance_ok):
    """Tryt to remove not existing imported module."""
    # Get all imported modules
    imported = sys.modules

    # Remove not existing module
    cvyt_logic_instance_ok.clean_sys_modules("abracadabra")

    # After clear
    after_clear = sys.modules

    assert len(imported) == len(after_clear)
