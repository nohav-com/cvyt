# -*- coding: utf-8 -*-
"""Help logic tests."""


def test_get_browser_flag(help_logic_instance_ok):
    """Get the browser flag(default is True)."""
    browser_flag = help_logic_instance_ok.get_use_browser()
    assert browser_flag is not None


def test_get_help_file_path_is_none(help_logic_instance_ok):
    """Get the path to the help file.

    Calling this method without calling get_info_from_config
    should return None.
    """
    help_path = help_logic_instance_ok.get_help_path()
    assert not help_path


def test_get_help_file_path_is_path(help_logic_instance_ok):
    """Get the path to the help file.
.
    It should return the file path.
    """
    help_logic_instance_ok.get_info_from_config()
    help_path = help_logic_instance_ok.get_help_path()
    assert help_path is not None
