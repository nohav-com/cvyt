# -*- coding: utf-8 -*-
"""
Provides the default content for the `app_config` file.
This approach avoids requiring an additional file to be shipped with the app.
If no config exists, the app will generate a new one from scratch.
"""


DEFAULT_CONFIG = {
    "name": "cvyt",
    "version": "0.0.1",
    "title": "CVYT by nohav.com",
    "author": "nohav.com",
    "contact": "nohav.com@gmail.com",
    "homepage": "www.nohav.com",
    "description": "Apps helps to use library cv2 in more user-friendly way.",
    "max_resolution": {
        "X": 3840,
        "Y": 2160
    },
    "config": {
        "tags": {
            "advanced": "==>",
            "level_up": ".."
        }
    },
    "create": [
        [
            "modules",
            "required"
        ]
    ],
    "update": {
        "modules": ["modules", "required"],
        "parts": [
            ["update", "modules"]
        ]
    },
    "modules": {
        "required": [
            "__init__.py",
            "module_config.json",
            "(.*)widget.py",
            "help.pdf"
        ],
        "required_other": [
            "name",
            "description",
            "update",
            "root",
            "class_mame"
        ],
        "config": "module_config.json",
        "root": "modules"
    },
    "app": {
        "root": ".",
        "config": "app_config.json"
    },
    "help": {
        "file": "main_help.pdf",
        "browser": 0,
        "tab": 1
    }
}
