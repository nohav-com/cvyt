"""Global conftest."""
import json
import shutil
import zipfile
from pathlib import Path

import pytest

from cvyt.common_update import CommonUpdate
from cvyt.config_logic import ConfigLogic
from cvyt.cvyt_logic import CvytLogic
from cvyt.default_app_config import DEFAULT_CONFIG
from cvyt.help.help_logic import HelpLogic
from cvyt.info.info_logic import InfoLogic
from cvyt.modules_available_logic import ModelAvailableModules
from cvyt.update.update_logic import UpdateLogic

REQUIRED_CHAIN_OF_KEYS = ["modules", "required"]
ROOT_CHAIN_OF_KEYS = ["modules", "root"]

DUMMY_MODULE_NAME = "dummy_module"

MAIN_CLASS_FILE_NAME = "dummy_module_widget.py"
MAIN_CLASS_CONTENT = """
__all__ = ['DummyModule']


class DummyModule():
   def __init__(self, **kwargs):
       pass

"""
MODULE_CONFIG_FILE_NAME = "module_config.json"
MODULE_CONFIG_CONTENT = {
    "name": "dummy_module",
    "version": "0.0.1",
    "description": "This is dummy module description"
}
MODULE_VERSION = "0.0.1"
MODULE_DESCRIPTION = "This is dummy module description"

ARCHIVE_DUMMY_NAME = "dummy_module_archive.zip"
ARCHIVE_DUMMY_OUTPUT = "dummy_archive_output"


@pytest.fixture(scope='function')
def config_logic_instance_default_config_file():
    """Default config logic instance.

    Using current app_config.json file.
    """
    logic = ConfigLogic()
    yield logic
    del logic


@pytest.fixture(scope='function')
def help_logic_instance_ok(config_logic_instance_default_config_file):
    """Help logic for help widget.

    Using default app_config.json
    """
    help_logic = HelpLogic(
        config=config_logic_instance_default_config_file,
        cwd=Path(__file__).parent)
    yield help_logic
    del help_logic


@pytest.fixture(scope='function')
def info_logic_instance_ok(config_logic_instance_default_config_file):
    """Info logic for info widget.

    Using default app_config.json
    """
    info_logic = InfoLogic(
        config=config_logic_instance_default_config_file
    )
    yield info_logic
    del info_logic


@pytest.fixture(scope='function')
def info_logic_instance_not_ok():
    """Info logic for info widget.

    Not passing instance of config object.
    """
    info_logic = InfoLogic()
    yield info_logic
    del info_logic


@pytest.fixture(scope='function')
def cvyt_logic_instance_ok():
    """Cvyt logic."""
    logic = CvytLogic()
    yield logic
    del logic


@pytest.fixture(scope='function')
def common_update_instance_ok(config_logic_instance_default_config_file):
    """Create common update instance."""
    common = CommonUpdate(config=config_logic_instance_default_config_file)
    yield common
    del common


@pytest.fixture(scope='function')
def create_update_logic(config_logic_instance_default_config_file):
    logic = UpdateLogic(config=config_logic_instance_default_config_file)
    yield logic
    del logic


@pytest.fixture(scope='function')
def get_required_chain_of_keys():
    """Get chain of keys to get list of required files."""
    yield REQUIRED_CHAIN_OF_KEYS


@pytest.fixture(scope='function')
def get_dummy_module_name():
    """Returns dummy module name."""
    yield DUMMY_MODULE_NAME


@pytest.fixture(scope='function')
def get_dummy_module_version():
    """Return dummy module version."""
    yield MODULE_VERSION


@pytest.fixture(scope='function')
def get_dummy_module_description():
    """Returns dummy module description."""
    yield MODULE_DESCRIPTION


@pytest.fixture(scope='function')
def create_dummy_module(tmp_path, config_logic_instance_default_config_file):
    """Create dummy module for testing purpose."""
    # New temp modules folder
    temp_modules = Path(tmp_path).joinpath("modules")
    temp_modules.mkdir()
    # Alter root folder for modules
    new_config_content = DEFAULT_CONFIG
    # Fill it with temp path
    new_config_content["modules"]["root"] = str(temp_modules)
    config_logic_instance_default_config_file.set_config_object(
        new_config_content)
    # Create available_modules instance
    available_modules = ModelAvailableModules(
        config=config_logic_instance_default_config_file
    )
    # Create folder
    folder_path = Path(temp_modules).joinpath(DUMMY_MODULE_NAME)
    Path(folder_path).mkdir()
    # Get list of required file from config
    required = config_logic_instance_default_config_file.get_value_for_key(
        REQUIRED_CHAIN_OF_KEYS)
    # Create files
    if required:
        for item in required:
            item_path = Path(folder_path).joinpath(item)
            with open(str(item_path), "w") as _:
                pass
    # Create main class + content
    main_class = Path(folder_path).joinpath(MAIN_CLASS_FILE_NAME)
    with open(main_class, "w", encoding="utf-8") as file_out:
        file_out.write(MAIN_CLASS_CONTENT)
    # Fill module_config file
    module_config = Path(folder_path).joinpath(MODULE_CONFIG_FILE_NAME)
    with open(str(module_config), "w", encoding='utf-8') as config_in:
        config_in.write(json.dumps(MODULE_CONFIG_CONTENT, indent=4))
    yield (temp_modules, available_modules)
    del available_modules
    # Clean
    if Path(tmp_path).exists():
        shutil.rmtree(tmp_path, ignore_errors=True)


@pytest.fixture(scope='function')
def create_modules_archive(
        create_dummy_module,
        config_logic_instance_default_config_file,
        get_required_chain_of_keys,
        create_update_logic):
    """Create modules archive."""
    temp_folder, _ = create_dummy_module
    assert temp_folder.exists()
    # Create modules archvie
    archive_path = Path(temp_folder).joinpath(ARCHIVE_DUMMY_NAME)
    # Get list of required file
    required = config_logic_instance_default_config_file.get_value_for_key(
        get_required_chain_of_keys)
    assert required is not None
    if required:
        with zipfile.ZipFile(str(archive_path), "w") as zip_in:
            for item in required:
                file_path = Path(temp_folder).joinpath(item)
                if file_path.exists():
                    zip_in.write(str(file_path))
    assert archive_path.exists()
    # Return path to archive
    yield archive_path
    # Clean
    if archive_path.exists():
        shutil.rmtree(str(archive_path), ignore_errors=True)
