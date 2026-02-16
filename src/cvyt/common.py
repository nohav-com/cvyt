# -*- coding: utf-8 -*-
"""Common logic for everything."""

import json
import logging

logger = logging.getLogger(__name__)


def convert_json_object_to_string(json_object: dict) -> str | None:
    """Convert json object to string.

    Args:
    json_object = json object to be converted

    Returns:
    String or None
    """
    string = None
    if json_object:
        try:
            string = json.dumps(json_object, indent=4)
        except Exception as e:
            logger.warning("Could not convert json to string(%s).", e)
        finally:
            return string


def convert_string_to_json_object(string: str):
    """Convert string to json object.

    Args:
    string = content of the file to convert

    Returns:
    json object(dict) or None
    """
    json_object = None
    if string:
        try:
            json_object = json.loads(string)
        except Exception as e:
            logger.warning(
                "Could not convert file conten to json object(%s).", e)
        finally:
            return json_object
