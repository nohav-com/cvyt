# -*- coding: utf-8 -*-
"""Info windows/widget."""

import logging
import webbrowser

from PySide6 import QtWidgets

from cvyt.info.info_logic import InfoLogic

__all__ = ['CreateInfoWindow']


logger = logging.getLogger(__name__)


class CreateInfoWindow(QtWidgets.QWidget):
    """Create simple info window/widget with information."""
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.logic = InfoLogic(*args, **kwargs)

        # Widget appearance
        self.add_title()

        # Layout
        self.main_layout = QtWidgets.QFormLayout(self)

        # Version
        self.version = QtWidgets.QLabel(self.logic.get_version())
        self.main_layout.addRow("Version:", self.version)

        # Name
        self.name = QtWidgets.QLabel(self.logic.get_name())
        self.main_layout.addRow("Name:", self.name)

        # Contact
        self.contact = QtWidgets.QLabel(self.logic.get_contact())
        # TODO
        # - localization
        self.main_layout.addRow("Contact:", self.contact)

        # Link to homepage
        self.link_to_home = QtWidgets.QLabel(self.logic.get_homepage())
        self.link_to_home.linkActivated.connect(self.home_page_open)
        self.main_layout.addRow("Homepage:", self.link_to_home)

        # Description
        self.description = QtWidgets.QLabel(self.logic.get_description())
        self.main_layout.addRow("Description:", self.description)

        # Add layout to main widget
        self.setLayout(self.main_layout)

    def add_version(self):
        """Add version item to widget."""
        self.version = QtWidgets.QLabel(self.logic.get_version())

    def home_page_open(self, link="Not working"):
        """Set possibility to open link in default browser."""
        try:
            webbrowser.open(link, new=1)
        except Exception as e:
            logger.warning(
                "Could not open link '%s' in browser(%s).", link, e)

    def add_title(self, title='Info'):
        """Add title to window/tab"""
        self.setWindowTitle(title)
