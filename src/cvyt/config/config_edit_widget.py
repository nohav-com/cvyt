# -*- coding: utf-8 -*-
"""A config edit widget."""

import logging

from PySide6 import QtCore, QtWidgets

__all__ = ['ConfigEditWindow']

# Title
WIDGET_TITLE = "Edit item"
# Labels
EDIT_FROM = "Edit from:"
NAME = "Name:"
VALUE = "Value:"
TYPE = "Type:"

# Description messages
DEFAULT_MSG = "Keep in mind what you are editing when a value needs to be entered."

logger = logging.getLogger(__name__)


class ConfigEditWindow(QtWidgets.QDialog):
    """Create a simple window for the 'Edit' operation on s config object.

    Kwargs:
    parent      = parent widget to attach the window to
    config      = config object to work with (editing, validation, etc.)
    edit        = key-value pair currently being edited
    edit_from   = string indicating what is being edited
    keys_chain  = chain of keys to navigate to the target location for
                  the operation
    index_item  = index of the item to be edited (used for lists)
    """
    def __init__(self, /, **kwargs):
        self.parent = kwargs.get("parent", None)
        self.config = kwargs.get("config", None)
        self.edit = kwargs.get("edit", None)
        self.edit_from = kwargs.get("edit_from", None)
        self.keys_chain = kwargs.get("keys_chain", [])
        self.item_index = kwargs.get("item_index", None)
        # Use the parent widget to initialize the dialog window
        super().__init__(self.parent)
        self.changes_page = QtWidgets.QWidget()
        self.changes_page_layout = QtWidgets.QVBoxLayout(self.changes_page)
        # Variables used to handle user input
        self.type_box = QtWidgets.QListWidget()
        self.name_box = QtWidgets.QTextEdit()
        self.value_box = QtWidgets.QTextEdit()
        # Global layout of the window
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        # Appearance
        self.setWindowTitle(WIDGET_TITLE)
        self.add_value_overview()
        self.add_cancel_ok_buttons()

        # Fill the list with value types that can be used
        self.set_available_types_of_value()
        # Set the current value type
        self.set_current_type_value()
        # Set a fixed size for the window
        self.resize(700, 300)
        # Let's roll
        self.exec()

    def reset_messages_to_default(self):
        """Reset all description messages/texts to their default values."""
        try:
            self.name_message.setText(DEFAULT_MSG)
            self.value_message.setText(DEFAULT_MSG)
            self.type_message.setText("")
        except Exception as e:
            logger.error("Could not reset all default messages (%s).", e)

    def set_message_to(self, part_id: QtWidgets.QLabel, message: str):
        """Set a message on a specific label.

        Args:
        id = label object
        message (str)= message to display
        """
        if part_id and message:
            try:
                part_id.setText(message)
            except Exception as e:
                logger.warning(
                    "Could not set message '%s' on '%s' because '%s'.",
                    message, part_id, e)

    def add_value_overview(self):
        """Simple overview with text boxes for Name (key), Value, and Type."""
        # Appearance
        edit_to_widget = QtWidgets.QWidget()
        edit_to_layout = QtWidgets.QHBoxLayout(edit_to_widget)
        edit_to_label = QtWidgets.QLabel(EDIT_FROM)
        edit_to_info = QtWidgets.QLabel(self.edit_from)
        edit_to_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        edit_to_layout.addWidget(edit_to_label)
        edit_to_layout.addWidget(edit_to_info)
        self.main_layout.addWidget(edit_to_widget)
        # Name
        name_widget = QtWidgets.QWidget()
        name_layout = QtWidgets.QHBoxLayout(name_widget)
        name_label = QtWidgets.QLabel(NAME)
        # Set the name - current
        if self.edit:
            self.name_box.setText(self.edit[0])
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_box)
        self.main_layout.addWidget(name_widget)
        # Add a name message
        self.name_message = QtWidgets.QLabel(DEFAULT_MSG)
        self.name_message.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.name_message)
        # Value
        value_widget = QtWidgets.QWidget()
        value_layout = QtWidgets.QHBoxLayout(value_widget)
        value_label = QtWidgets.QLabel(VALUE)
        # Set the value - current
        if self.edit:
            self.value_box.setText(self.edit[1])
        value_layout.addWidget(value_label)
        value_layout.addWidget(self.value_box)
        self.main_layout.addWidget(value_widget)
        # Add a value message
        self.value_message = QtWidgets.QLabel(DEFAULT_MSG)
        self.value_message.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.value_message)
        # Type
        type_widget = QtWidgets.QWidget()
        type_layout = QtWidgets.QHBoxLayout(type_widget)
        type_label = QtWidgets.QLabel(TYPE)
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_box)
        self.main_layout.addWidget(type_widget)
        # Add a error message
        self.type_message = QtWidgets.QLabel()
        self.type_message.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.type_message)
        # Connect to the methods
        self.type_box.itemClicked.connect(self.type_value_selection_changed)

    def type_value_selection_changed(self):
        """Selection type changed."""
        item = self.type_box.currentItem()
        if item:
            item_type = item.text()
            help_message = self.config.get_value_type_help(item_type)
            if help_message:
                self.type_message.setText(help_message)

    def set_current_type_value(self):
        """Set the current value type."""
        if self.edit:
            items = self.type_box.findItems(
                self.edit[2], QtCore.Qt.MatchFlag.MatchExactly
            )
            if items:
                self.type_box.setCurrentItem(items[-1])
                self.type_value_selection_changed()

    def set_available_types_of_value(self):
        """Set a list of available/alowed value types."""
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
        """Collect input values, validate them, and apply to the config."""
        name = self.name_box.toPlainText()
        value = self.value_box.toPlainText()
        value_type = self.type_box.currentItem().text()
        # Convert value to the proper format(based on its type)
        converted_value = self.config.convert_value_to_type(value_type, value)

        # Reset messages and descriptions
        self.reset_messages_to_default()

        # Validate
        can_apply, name_msg, value_msg, type_msg = \
            self.config.can_i_apply_changed(
                name, converted_value, value_type, self.edit_from
            )

        # Changes can be applied
        if can_apply:
            status = self.config.apply_to_config(
                keys_chain=self.keys_chain,
                edit=(name, converted_value),
                item_index=self.item_index
            )
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
