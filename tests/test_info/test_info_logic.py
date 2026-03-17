# -*- coding: utf-8 -*-
"""Info logic tests."""

# Variable
UNKNOWN = "UNKNOWN"


def test_info_logic_get_name_ok(info_logic_instance_ok):
    """Get the name from the app config file."""
    name = info_logic_instance_ok.get_name()
    assert name


def test_info_logic_get_name_not_ok(info_logic_instance_not_ok):
    """Get the name from the app config file.

    Expected result: 'UNKNOWN'."""
    name = info_logic_instance_not_ok.get_name()
    assert name == UNKNOWN


def test_info_logic_get_version_ok(info_logic_instance_ok):
    """Get the version of the app from the config file."""
    version = info_logic_instance_ok.get_version()
    assert version is not None


def test_info_logic_get_version_not_ok(info_logic_instance_not_ok):
    """Get the version of the app from the config file."""
    version = info_logic_instance_not_ok.get_version()
    assert version == UNKNOWN


def test_info_logic_get_contact_ok(info_logic_instance_ok):
    """Get the contact from the config file."""
    contact = info_logic_instance_ok.get_contact()
    assert contact is not None


def test_info_logic_get_contact_not_ok(info_logic_instance_not_ok):
    """Get the contact from the config file."""
    contact = info_logic_instance_not_ok.get_contact()
    assert contact == UNKNOWN


def test_info_logic_get_homepage_ok(info_logic_instance_ok):
    """Get the homepage from the config file."""
    homepage = info_logic_instance_ok.get_homepage()
    assert homepage is not None


def test_info_logic_get_homepage_not_ok(info_logic_instance_not_ok):
    """Get the homepage from the config file.

    Expected result: 'UNKNOWN'
    """
    homepage = info_logic_instance_not_ok.get_homepage()
    assert homepage == UNKNOWN


def test_info_logic_get_description_ok(info_logic_instance_ok):
    """Get the description from the config file."""
    description = info_logic_instance_ok.get_description()
    assert description is not None


def test_info_logic_get_description_no_ok(info_logic_instance_not_ok):
    """Get the description from the config file.

    Expected result: 'UNKNOWN'"""
    description = info_logic_instance_not_ok.get_description()
    assert description == UNKNOWN
