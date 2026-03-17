# -*- coding: utf-8 -*-
"""Widget to view and edit the config file."""

import copy
import logging
from pathlib import Path

from PySide6 import QtCore, QtWidgets

from cvyt.config.config_add_widget import ConfigAddWindow
from cvyt.config.config_edit_widget import ConfigEditWindow

__all__ = ['CreateConfigWindow']

logger = logging.getLogger(__name__)


class CreateConfigWindow(QtWidgets.QWidget):
    """Creating a window/widget for operations on a config object.

    Kwargs:
    config = config object
    """
    def __init__(self, /, **kwargs):
        super().__init__()
        self.config = kwargs.get('config', None)
        # Working config (modified and used with "Save"))
        self.working_config = None
        # Make a deep copy of the config object
        self.copy_main_config_to_working_config()
        # Global variables
        self.keys_chain = []
        self.indexes_chain = []
        # # Widget to store config file levels (original is in JSON format)
        self.config_overview = QtWidgets.QTreeWidget()
        self.config_overview.setHeaderLabels(["Name", "Value"])

        # Default in, out path boxes
        self.in_config_textbox = None
        self.out_config_textbox = None

        # Main layout
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.main_layout)

        # Appearance
        self.add_title()
        # Add description from the config
        self.add_description()
        # Add config in, out UI section
        self.add_config_in_out()
        # Add the add btn
        self.add_config_level_path()
        # Set the default value
        self.set_default_config_in_out_path()
        # Add the overview + edit btn
        self.add_config_overview()
        # Add the config detail
        self.add_config_detail()
        # Add the "Save" section
        self.add_save_config_changes()

    def copy_main_config_to_working_config(self):
        """Copy the main config to the working copy."""
        if self.config:
            self.working_config = copy.deepcopy(self.config)
        else:
            logger.warning("No config object found to copy.")

    def set_default_config_in_out_path(self):
        """Set default values for in, out config paths."""
        # Get the path to the config file
        config_path = self.config.get_config_path()
        if config_path:
            self.out_config_textbox.insertPlainText(config_path)
            self.in_config_textbox.insertPlainText(config_path)
            self.show_key_value_list()
        else:
            logger.warning("Could not find the path to the config file.")

    def add_config_level_path(self):
        """Level/path of the config file content at the current cursor
        position."""
        # Appearance
        self.level_path = QtWidgets.QWidget()
        level_path_layout = QtWidgets.QHBoxLayout(self.level_path)
        self.config_deep_path = QtWidgets.QLabel()
        level_path_layout.addWidget(self.config_deep_path)

        self.main_layout.addWidget(self.level_path)

    def show_key_value_list(self):
        """Show the current level of the config file."""
        # Get the level info(list of keys, values)
        values_raw, self.keys_chain = self.working_config.get_list_of_keys(
            self.keys_chain)

        # Clear the old "level"
        self.config_deep_path.clear()
        # Show the new level/path of the config
        self.config_deep_path.setText(
            self.working_config.create_config_deep_path(self.keys_chain))

        values = []
        # Transform values into widget items
        for item in values_raw:
            value = QtWidgets.QTreeWidgetItem([item[0], str(item[1])])
            value.setToolTip(0, str(item[0]))
            value.setToolTip(1, str(item[1]))
            values.append(value)

        # Ok, let's show them
        if values:
            self.config_overview.clear()
            self.config_overview.insertTopLevelItems(0, values)

    def clear_config_detail(self):
        """Clear the config detail."""
        # Name
        self.name_detail_value.clear()
        # Value
        self.value_detail_value.clear()

    def config_item_selected(self, item: str):
        """Item in the config overview selected + double clicked.

        Navigates deeper or up to the next level of the config.

        Args:
        item (str)= the selected item
        """
        # Get the info from the UI
        key = item.text(0).split("|-")[-1]
        value = item.text(1)
        # Validate whether it can go deeper (list or dict)
        if key and value and self.working_config.let_through(key, value):
            # Check if we need to go down or up
            if self.working_config.go_level_up(key):
                # Up
                if self.keys_chain:
                    self.keys_chain.pop(-1)
            else:
                # Down
                self.keys_chain.append(key)
            # Let's show the new level
            self.show_key_value_list()
        else:
            logger.info(
                "Cannot go deeper for this key-value pair %s, %s",
                key, value)

    def config_overview_item_changed(self, item):
        """Item changed in config overview, show details

        Args:
        item = the selected item
        """
        # Get the info from the UI
        key = item.text(0).split("|-")[-1]
        value = item.text(1)

        # Get the position(row) from the config_overview
        current_row = self.config_overview.currentIndex()

        if current_row:
            current_row = current_row.row()

        # We can proceed
        if key and value:
            # Temp key chain
            key_chain = [] + self.keys_chain
            key_chain.append(key)
            # Get the actual value from the config object
            current_value = self.working_config.get_value_for_key(
                key_chain, index=current_row-1)
            # Set the name and value
            self.set_name_config_detail(key)
            self.set_value_config_detail(value)
            # Set the actual type of value
            self.set_type_config_detail(type(current_value).__name__)

    def set_type_config_detail(self, type_value):
        """Set the value type in the config detail

        Args:
        type_value = the type of the value
        """
        if type_value:
            # Convert the type to a string for presentation to the user
            name = self.working_config.get_name_for_type(type_value)
            items = self.types_detail_value.findItems(
                name, QtCore.Qt.MatchFlag.MatchExactly)

            # Found the name in the list of available types
            if items:
                self.types_detail_value.setCurrentItem(items[-1])
            else:
                logger.info("Unknown value type for '%s'.", type_value)

    def add_btn_operation(self):
        """'Add' value operation. Create and open the window."""
        # Get the selected item
        current_item = self.config_overview.currentItem()
        if current_item:
            # Get the key and value
            key = current_item.text(0).split("|-")[-1]
            value = current_item.text(1)
            # Get the index/position as well
            current_row = self.config_overview.currentIndex()

            # Expecting to be at '..' or '.'
            if key in ['.', '..'] \
                    and value in ['.', '..'] and current_row.row() == 0:
                # Temp copy of the keys chain
                keys_chain = [] + self.keys_chain
                # Get the current value(level)
                current_value = self.working_config.get_value_for_key(
                    keys_chain)
                # Current type
                current_value_type_name = type(current_value).__name__
                # Open the 'add' window
                _ = ConfigAddWindow(
                    parent=self,
                    config=self.working_config,
                    add_to=current_value_type_name,
                    keys_chain=keys_chain
                )
            else:
                message = QtWidgets.QMessageBox(self)
                message.about(
                    self,
                    "Error - add",
                    "No position selected to place the new item.\
                    If you want to add a new item to the config, please\
                    select '.' or '..' and click '+'.")
        else:
            message = QtWidgets.QMessageBox(self)
            message.about(
                self,
                "Error - add",
                "No position selected to place the new item.\
                    If you want to add a new item to the config, please\
                    select '.' or '..' and click '+'.")

    def edit_btn_operation(self):
        """'Edit' item operation. Create and open the window."""
        # Get the current item.
        current_item = self.config_overview.currentItem()
        if current_item:
            # Get the key and value
            key = current_item.text(0).split("|-")[-1]
            value = current_item.text(1)
            # Get the value type from the UI
            value_type = self.types_detail_value.currentItem()
            # Get the current index(in case list)
            current_row = self.config_overview.currentIndex()

            # Expecting that cursor NOT to be at '..' or '.'
            if key not in ['.', '..'] \
                    and value not in ['.', '..'] and current_row.row() > 0:
                # Temp copy of the key chain
                keys_chain = [] + self.keys_chain
                keys_chain.append(key)

                # Get the actual value from the config
                current_value = self.working_config.get_value_for_key(
                    keys_chain, index=current_row.row()-1)
                # Value type
                current_value_type_name = type(current_value).__name__
                # Can this value be edited? → Not a list or dict directly
                if self.working_config.can_i_edit_object_of_type(
                    current_value_type_name
                ):
                    _ = ConfigEditWindow(
                        parent=self,
                        config=self.working_config,
                        edit_from=current_value_type_name,
                        edit=(
                            key,
                            value,
                            value_type.text()
                        ),
                        keys_chain=keys_chain,
                        item_index=current_row.row() - 1
                    )
                else:
                    message = QtWidgets.QMessageBox(self)
                    message.about(
                        self,
                        "Error - edit",
                        "Only simple types (int, string, etc.) can be edited.")
            else:
                message = QtWidgets.QMessageBox(self)
                message.about(
                    self,
                    "Error - edit",
                    """Please select an item to be edited, except the pairs
                    '.' + '.' or '..' + '..'.""")
        else:
            message = QtWidgets.QMessageBox(self)
            message.about(
                self,
                "Error - edit",
                "No item selected for editing.")

    def remove_btn_operation(self):
        """Remove the selected item from the config object."""
        # Get the selected item
        current_item = self.config_overview.currentItem()
        # Get the index
        current_row = self.config_overview.currentIndex()
        if current_item:
            # Get the key
            key = current_item.text(0).split("|-")[-1]
            # Temp copy of the key chain
            key_chain = [] + self.keys_chain
            key_chain.append(key)
            # Preparation for the "are you sure" message box
            are_u_sure = QtWidgets.QMessageBox(self)
            are_u_sure.setWindowTitle("Remove")
            # Message
            are_u_sure.setText(
                "Do you want to remove the value for this key? If so, click 'OK'\
                and then 'Save'.")
            # Set the key chain in  the message box
            are_u_sure.setInformativeText(f"{'->'.join(key_chain)}")
            # Add OK, Cancel btns.
            are_u_sure.setStandardButtons(
                QtWidgets.QMessageBox.StandardButton.Ok |
                QtWidgets.QMessageBox.StandardButton.Cancel
            )
            # Default btn
            are_u_sure.setDefaultButton(
                QtWidgets.QMessageBox.StandardButton.Ok)
            # Let's roll
            result = are_u_sure.exec()
            # Process the result
            if result == QtWidgets.QMessageBox.StandardButton.Ok:
                status = self.working_config.apply_to_config(
                    key_chain,
                    remove=True,
                    item_index=current_row.row() - 1)
                # Not ok
                if status:
                    # Show the message - something went wrong
                    logger.error(
                        "Attempt to remove item '%s' failed(see log file).",
                        key)
                # Update the overview
                self.show_key_value_list()
                # Clear the key and value detail
                self.clear_config_detail()
        else:
            message = QtWidgets.QMessageBox(self)
            message.about(
                self,
                "Remove",
                "No item selected for removal.")

    def add_config_detail(self):
        """Add the config detail group."""
        # Name
        name_detail_part = QtWidgets.QWidget()
        name_detail_layout = QtWidgets.QHBoxLayout(name_detail_part)
        name_detail_label = QtWidgets.QLabel("Name:")
        self.name_detail_value = QtWidgets.QTextEdit()
        self.name_detail_value.setReadOnly(True)
        # Add to the layout
        name_detail_layout.addWidget(name_detail_label)
        name_detail_layout.addWidget(self.name_detail_value)
        # Value + type
        value_detail_part = QtWidgets.QWidget()
        value_detail_layout = QtWidgets.QHBoxLayout(value_detail_part)
        value_detail_label = QtWidgets.QLabel("Value:")
        value_detail_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.value_detail_value = QtWidgets.QTextEdit()
        self.value_detail_value.setReadOnly(True)
        type_detail_label = QtWidgets.QLabel("Type:")
        type_detail_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.types_detail_value = QtWidgets.QListWidget()
        # Set all available types
        self.set_available_types_of_value()
        # Add to the layout
        value_detail_layout.addWidget(value_detail_label)
        value_detail_layout.addWidget(self.value_detail_value)
        value_detail_layout.addWidget(type_detail_label)
        value_detail_layout.addWidget(self.types_detail_value)
        # Overview config detail layout
        overview_config_detail_layout = QtWidgets.QVBoxLayout()
        overview_config_detail_layout.addWidget(name_detail_part)
        overview_config_detail_layout.addWidget(value_detail_part)
        # Group box
        config_detail_group = QtWidgets.QGroupBox("Config detail")
        config_detail_group.setCheckable(False)
        config_detail_group.setLayout(overview_config_detail_layout)
        # Add it to the main layout
        self.main_layout.addWidget(config_detail_group)

    def add_save_config_changes(self):
        """Add the save config changes button."""
        self.save_btn_part = QtWidgets.QWidget()
        save_btn_layout = QtWidgets.QHBoxLayout(self.save_btn_part)
        # Position
        save_btn_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        save_btn = QtWidgets.QPushButton("Save")
        # Appearance
        save_btn.setMaximumWidth(50)

        save_btn.clicked.connect(self.save_btn_operation)
        save_btn_layout.addWidget(save_btn)
        self.main_layout.addWidget(self.save_btn_part)

    def set_name_config_detail(self, name):
        """Set the name to the config detail.

        Args:
        name = name
        """
        if name:
            self.name_detail_value.clear()
            self.name_detail_value.setText(str(name))

    def set_available_types_of_value(self):
        """Set the list of available/allowed value types."""
        for item in self.working_config.get_list_of_type_names():
            list_item = QtWidgets.QListWidgetItem(item)
            self.types_detail_value.addItem(list_item)

    def set_value_config_detail(self, value):
        """Set the value to the config detail.

        Args:
        value = value
        """
        if value:
            self.value_detail_value.clear()
            self.value_detail_value.setText(str(value))

    def add_config_overview(self):
        """Add the config overview + add, remove, edit buttons."""
        config_overview_layout = QtWidgets.QHBoxLayout()
        config_group = QtWidgets.QGroupBox("Config")
        config_group.setCheckable(False)
        config_group.setLayout(config_overview_layout)

        edit_operation_part = QtWidgets.QWidget()
        edit_operation_layout = QtWidgets.QVBoxLayout(edit_operation_part)
        # Add btn
        edit_operation_add_btn = QtWidgets.QPushButton("+")
        # Style
        edit_operation_add_btn.setMaximumWidth(25)
        # Edit btn
        edit_operation_edit_btn = QtWidgets.QPushButton("Edit")
        # Style
        edit_operation_edit_btn.setMaximumWidth(55)
        # Remove btn
        edit_operation_remove_btn = QtWidgets.QPushButton("-")
        # Appearance
        edit_operation_remove_btn.setMaximumWidth(25)

        edit_operation_edit_btn.setToolTip(
            "Remove the value for the selected key in the config.")
        edit_operation_layout.addWidget(edit_operation_add_btn)
        edit_operation_layout.addWidget(edit_operation_edit_btn)
        edit_operation_layout.addWidget(edit_operation_remove_btn)

        # Set the position of the btns inside the layout
        edit_operation_layout.itemAt(0).setAlignment(
            QtCore.Qt.AlignmentFlag.AlignTop)
        edit_operation_layout.itemAt(1).setAlignment(
            QtCore.Qt.AlignmentFlag.AlignCenter)
        edit_operation_layout.itemAt(2).setAlignment(
            QtCore.Qt.AlignmentFlag.AlignBottom)

        config_overview_layout.addWidget(self.config_overview)
        config_overview_layout.addWidget(edit_operation_part)
        edit_operation_edit_btn.clicked.connect(self.edit_btn_operation)
        edit_operation_remove_btn.clicked.connect(self.remove_btn_operation)
        edit_operation_add_btn.clicked.connect(self.add_btn_operation)

        # Connect methods
        self.config_overview.itemDoubleClicked.connect(
            self.config_item_selected)
        self.config_overview.itemClicked.connect(
            self.config_overview_item_changed)

        self.main_layout.addWidget(config_group)

    def save_btn_operation(self):
        """Save the config object to the config file."""
        # Store the "working" config object into the "real" config object
        self.config.set_config_object(
            self.working_config.get_config_object())
        # Can the object be saved to the output config file?
        if self.out_config_textbox:
            saved = self.config.save_config(
                self.out_config_textbox.toPlainText())
            if not saved:
                message = QtWidgets.QMessageBox(self)
                message.about(
                    self,
                    "Error - save",
                    "Config file was not saved. See the log file.")
        else:
            message = QtWidgets.QMessageBox(self)
            message.about(
                self,
                "Error - save",
                "No output config file set, can not store the config.")
        self.show_key_value_list()

    def add_description(self):
        """Add the description from the config file"""
        # Get the description
        description = self.working_config.get_description()
        if description:
            description_layout = QtWidgets.QVBoxLayout()
            # Groupbox
            description_group = QtWidgets.QGroupBox("Description")
            description_group.setCheckable(False)
            description_group.setLayout(description_layout)
            description_box = QtWidgets.QLabel(
                description)
            description_layout.addWidget(description_box)

            self.main_layout.addWidget(description_group)

    def select_config_in_operation(self):
        """Select the config file 'in'(to be changed)."""
        dialog = QtWidgets.QFileDialog(self)
        dialog.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFile)
        file_name, _ = dialog.getOpenFileName()
        if file_name:
            if Path(file_name).exists():
                self.in_config_textbox.clear()
                self.in_config_textbox.insertPlainText(file_name)
                # Clear all necessary items
                self.out_config_textbox.clear()
                self.config_overview.clear()
                # Load the config from a new file
                self.config.load_config(file_name)
                self.copy_main_config_to_working_config()
                # Set all required items
                self.out_config_textbox.insertPlainText(file_name)
                self.show_key_value_list()

    def add_config_in_out(self):
        """Add the config in/out overview."""
        # Config in
        config_in = QtWidgets.QWidget()
        config_in_layout = QtWidgets.QHBoxLayout(config_in)
        config_in_label = QtWidgets.QLabel("In:")
        config_in_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        config_in_layout.addWidget(config_in_label)
        self.in_config_textbox = QtWidgets.QTextEdit()
        self.in_config_textbox.setReadOnly(True)
        config_in_layout.addWidget(self.in_config_textbox)
        config_in_search_btn = QtWidgets.QPushButton("File")
        config_in_search_btn.setMaximumWidth(50)
        config_in_layout.addWidget(config_in_search_btn)
        # Config out
        config_out = QtWidgets.QWidget()
        config_out_layout = QtWidgets.QHBoxLayout(config_out)
        config_out_label = QtWidgets.QLabel("Out:")
        config_out_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        config_out_layout.addWidget(config_out_label)
        self.out_config_textbox = QtWidgets.QTextEdit()
        self.out_config_textbox.setReadOnly(True)
        config_out_layout.addWidget(self.out_config_textbox)
        config_out_search_btn = QtWidgets.QPushButton("File")
        config_out_search_btn.setMaximumWidth(50)
        config_out_layout.addWidget(config_out_search_btn)
        # Group box
        config_in_out_layout = QtWidgets.QVBoxLayout()
        config_in_out_layout.addWidget(config_in)
        config_in_out_layout.addWidget(config_out)
        config_in_out_group = QtWidgets.QGroupBox("Config in/out")
        config_in_out_group.setCheckable(False)
        config_in_out_group.setLayout(config_in_out_layout)
        # Pin it to the main layout
        self.main_layout.addWidget(config_in_out_group)
        # Connect
        config_in_search_btn.clicked.connect(self.select_config_in_operation)
        config_out_search_btn.clicked.connect(self.select_config_out_operation)

    def select_config_out_operation(self):
        """Select the config file 'out'(to be stored in)."""
        dialog = QtWidgets.QFileDialog(self)
        dialog.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFile)
        file_name, _ = dialog.getOpenFileName()
        if file_name:
            if Path(file_name).exists():
                self.out_config_textbox.clear()
                self.out_config_textbox.insertPlainText(file_name)

    def add_title(self, title='Configuration'):
        """Add a title to the window/widget."""
        # Add title to window/widget
        self.setWindowTitle(title)
