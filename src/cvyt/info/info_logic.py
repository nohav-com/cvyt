# -*- coding: utf-8 -*-
"""Logic for info window/widget."""

import logging

__all__ = ['InfoLogic']

# No value founded
UNKNOWN = "UNKNOWN"

logger = logging.getLogger(__name__)


class InfoLogic():
    """Basic logic supporting info window/widget"""
    def __init__(self, /, **kwargs):
        self.config = kwargs.get('config', None)

    def get_name(self) -> str:
        """Get name of the app."""
        return self.config.get_name() if self.config else UNKNOWN

    def get_version(self) -> str:
        """Get version of the app."""
        return self.config.get_version() if self.config else UNKNOWN

    def get_contact(self) -> str:
        """Get contact."""
        return self.config.get_contact() if self.config else UNKNOWN

    def get_homepage(self) -> str:
        """Get homepage of the app."""
        homepage = self.config.get_homepage() if self.config else None
        if homepage:
            return "<a href='%s'>%s</a>" % (homepage, homepage)
        else:
            return UNKNOWN

    def get_description(self) -> str:
        """Get a description of the app."""
        return self.config.get_description() \
            if self.config else UNKNOWN
