# -*- coding: utf-8 -*-
"""Add widget."""

import logging

from PySide6 import QtCore, QtWidgets

__all__ = ['ConfigAddWindow']

# Window title
WIDGET_TITLE = "Add item"
# Labels
ADD_TO = "Add to:"
NAME = "Name:"
VALUE = "Value:"
TYPE = "Type:"

# Description messages
DEFAULT_MSG = "Keep it mind what you are adding(when value needs to be filled)"

logger = logging.getLogger(__name__)


class ConfigAddWindow(QtWidgets.QDialog):
    """Create simple window for operation 'Add' over config object.

    Its separated from 'Edit' for clarity and few differences.

    Kwargs:
    parent = parent widget to tie the window to
    config = config object to work with(add, validation, etc.)
    add_to = string saying we are adding new item to
    keys_chain = chain of keys to navigate where to do the operation
    """
    def __init__(self, /, **kwargs):
        self.parent = kwargs.get("parent", None)
        self.config = kwargs.get("config", None)
        self.add_to = kwargs.get("add_to", "Unknown")
        self.keys_chain = kwargs.get("keys_chain", [])

        # Use parent widget to init dialog window
        super().__init__(self.parent)
        self.changes_page = QtWidgets.QWidget()
        self.changes_page_layout = QtWidgets.QVBoxLayout(self.changes_page)
        # Variables - used to manipulate input from user
        self.type_box = QtWidgets.QListWidget()
        self.name_box = QtWidgets.QTextEdit()
        self.value_box = QtWidgets.QTextEdit()
        # Global layout for window
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        # Appereance
        self.setWindowTitle(WIDGET_TITLE)
        self.add_value_overview()
        self.add_cancel_ok_buttons()

        # Fill the list with available types of value which can be used
        self.set_available_types_of_value()
        # Fixed size of the window
        self.resize(700, 300)
        # Lets roll
        self.exec()

    def reset_messages_to_default(self):
        """Reset all description's messages/texts to default value."""
        try:
            self.name_message.setText(DEFAULT_MSG)
            self.value_message.setText(DEFAULT_MSG)
            self.type_message.setText("")
        except Exception as e:
            logger.error("Could not reset all default messages(%s).", e)

    def set_message_to(self, part_id: QtWidgets.QLabel, message: str):
        """Set message to specific label.

        Args:
        id = lable object
        message = message to show
        """
        if part_id and message:
            try:
                part_id.setText(message)
            except Exception as e:
                logger.warning(
                    "Could not set message '%s' to '%s' because '%s'",
                    message, part_id, e)

    def add_value_overview(self):
        """Simple overview with name(key), value, type textboxes to fill."""
        # Appearance
        add_to_widget = QtWidgets.QWidget()
        add_to_layout = QtWidgets.QHBoxLayout(add_to_widget)
        add_to_label = QtWidgets.QLabel(ADD_TO)
        add_to_info = QtWidgets.QLabel(self.add_to)
        add_to_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        add_to_layout.addWidget(add_to_label)
        add_to_layout.addWidget(add_to_info)
        self.main_layout.addWidget(add_to_widget)
        # Name
        name_widget = QtWidgets.QWidget()
        name_layout = QtWidgets.QHBoxLayout(name_widget)
        name_label = QtWidgets.QLabel(NAME)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_box)
        self.main_layout.addWidget(name_widget)
        # Add name message
        self.name_message = QtWidgets.QLabel(DEFAULT_MSG)
        self.name_message.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.name_message)
        # Value
        value_widget = QtWidgets.QWidget()
        value_layout = QtWidgets.QHBoxLayout(value_widget)
        value_label = QtWidgets.QLabel(VALUE)
        value_layout.addWidget(value_label)
        value_layout.addWidget(self.value_box)
        self.main_layout.addWidget(value_widget)
        # Add value message
        self.value_message = QtWidgets.QLabel(DEFAULT_MSG)
        self.value_message.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.value_message)
        # Types
        type_widget = QtWidgets.QWidget()
        type_layout = QtWidgets.QHBoxLayout(type_widget)
        type_label = QtWidgets.QLabel(TYPE)
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_box)
        self.main_layout.addWidget(type_widget)
        # Add error message
        self.type_message = QtWidgets.QLabel("")
        self.type_message.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.type_message)
        # Connect methods
        self.type_box.itemClicked.connect(self.type_value_selection_changed)

    def type_value_selection_changed(self):
        """Selection of type changed."""
        item = self.type_box.currentItem()
        if item:
            item_type = item.text()
            help_message = self.config.get_value_type_help(item_type)
            if help_message:
                self.type_message.setText(help_message)

    def set_available_types_of_value(self):
        """Set list of available/alowed types of values."""
        for item in self.config.get_list_of_type_names():
            list_item = QtWidgets.QListWidgetItem(item)
            self.type_box.addItem(list_item)

    def add_cancel_ok_buttons(self):
        """Add confirm and cancel buttons."""
        # Confirm of cancel
        btns_cancel_ok = (
            QtWidgets.QDialogButtonBox.Ok
            | QtWidgets.QDialogButtonBox.Cancel
        )

        button_box = QtWidgets.QDialogButtonBox(btns_cancel_ok)
        button_box.accepted.connect(self.accept_ok)
        button_box.rejected.connect(self.reject)

        self.main_layout.addWidget(button_box)

    def accept_ok(self):
        """Collect values(inputs), validate and apply them to config."""
        name = self.name_box.toPlainText()
        value = self.value_box.toPlainText()
        value_type = self.type_box.currentItem().text() \
            if self.type_box.currentItem() else None
        # Convert value to proper format(based on type of value)
        converted_value = self.config.convert_value_to_type(value_type, value)

        # Reset messages/descriptions
        self.reset_messages_to_default()

        # Validate
        can_apply, name_msg, value_msg, type_msg = \
            self.config.can_i_apply_changed(
                name, converted_value, value_type, self.add_to
            )

        # Changes can be applied
        if can_apply:
            # Reset default messages
            self.reset_messages_to_default()
            # Apply changes
            status = self.config.apply_to_config(
                keys_chain=self.keys_chain,
                add=(name, converted_value)
            )
            # Everything is ok, reload overview
            if status:
                self.parent.show_key_value_list()
            else:
                # Problem, simple error message
                logger.error(
                    "Attemp to add item to config failed. Check log file.")
            self.accept()
        else:
            # Show messages for name, value, type
            self.set_message_to(self.name_message, name_msg)
            self.set_message_to(self.value_message, value_msg)
            self.set_message_to(self.type_message, type_msg)
