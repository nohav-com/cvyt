def test_get_browser_flag(help_logic_instance_ok):
    """Get browser flag(default is True)."""
    browser_flag = help_logic_instance_ok.get_use_browser()
    assert browser_flag is not None


def test_get_help_file_path_is_none(help_logic_instance_ok):
    """Get path to help file.

    Calling method without calling get_info_from_config.
    Expecting None as answer.
    """
    help_path = help_logic_instance_ok.get_help_path()
    assert not help_path


def test_get_help_file_path_is_path(help_logic_instance_ok):
    """Get path to help file.
.
    Expecting None as answer.
    """
    help_logic_instance_ok.get_info_from_config()
    help_path = help_logic_instance_ok.get_help_path()
    assert help_path is not None
