from pathlib import Path
from cvyt.common import (
    convert_json_object_to_string,
    convert_string_to_json_object
)
from cvyt.default_app_config import DEFAULT_CONFIG


def test_get_json_content_valid(tmp_path):
    """Try to convert valid json file"""
    # Prepare file
    file_path = Path(tmp_path).joinpath("dummy.json")
    with open(str(file_path), "w", encoding='utf-8') as file_in:
        file_in.write(convert_json_object_to_string(DEFAULT_CONFIG))
    # Read the json
    config_again = None
    with open(str(file_path), "r", encoding='utf-8') as file_again:
        config_again = convert_string_to_json_object(file_again.read())

    assert config_again is not None
    assert DEFAULT_CONFIG == config_again


def test_get_json_content_not_valid(tmp_path):
    """Try to convert not valid json file."""
    # Prepare file
    file_path = Path(tmp_path).joinpath("dummy.json")
    with open(str(file_path), "w") as _:
        pass

    # Read the json
    config_again = None
    with open(str(file_path), "r", encoding='utf-8') as file_again:
        config_again = convert_string_to_json_object(file_again.read())
    assert not config_again
