# -*- coding: utf-8 -*-
"""
Default content of app_config file. Done this way to avoid nessecity to
ship this app with extra file(default config and config it self).
It means if necesseraly app will create new config from scratch.
"""


DEFAULT_CONFIG = {
    "name": "cvyt",
    "version": "0.0.1",
    "title": "CVYT by nohav.com",
    "author": "nohav.com",
    "contact": "nohav.com@gmail.com",
    "homepage": "www.nohav.com",
    "description": "Use cv2 in friendly way.",
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
