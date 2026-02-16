# -*- coding: utf-8 -*-
"""Update window/widget."""

import datetime
import logging
from pathlib import Path

from PySide6 import QtCore, QtWidgets

from cvyt.update.update_logic import UpdateLogic

__all__ = ['CreateUpdateWindow']


logger = logging.getLogger(__name__)


class CreateUpdateWindow(QtWidgets.QWidget):
    """Creating window/widget for update."""
    def __init__(self, /, **kwargs):
        super().__init__()
        self.logic = UpdateLogic(**kwargs)

        # # Create/check temp folders for update purposes
        # self.logic.create_temp_folders()

        # Main layout
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.main_layout)

        # Global items
        self.select_box = None
        self.select_modules_description = None
        self.show_content_archive = None

        # Widget appearance
        self.add_title()
        self.add_select_archive()
        self.add_show_archive_content()
        self.add_select_modules_for_update()
        self.add_start_update()
        self.add_logs()

    def add_title(self, title='Update - cvyt'):
        # Add title to window/widget
        self.setWindowTitle(title)

    def add_select_archive(self):
        """Select archive."""
        select_archive_layout = QtWidgets.QHBoxLayout()
        select_archive_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        # Select the archive
        self.select_textbox = QtWidgets.QTextEdit()
        self.select_textbox.setReadOnly(True)
        self.select_textbox.setMaximumHeight(30)
        # From folder
        select_btn = QtWidgets.QPushButton("Folder")
        # Appearance
        select_btn.setMaximumWidth(60)

        # select_archive_layout.addWidget(select_label)
        select_archive_layout.addWidget(self.select_textbox)
        select_archive_layout.addWidget(select_btn)
        # Select archove group
        select_archive_group = QtWidgets.QGroupBox("Select archive:")
        select_archive_group.setCheckable(False)
        select_archive_group.setLayout(select_archive_layout)

        # Connect
        select_btn.clicked.connect(self.select_update_archive)
        # Add to main layout
        self.main_layout.addWidget(select_archive_group)

    def add_show_archive_content(self):
        """Show archive content"""
        # Show content of selected archive
        self.show_content_archive = QtWidgets.QWidget()
        show_archive_layout = QtWidgets.QHBoxLayout(
            self.show_content_archive)
        # Use everything
        self.select_all = QtWidgets.QCheckBox("Select all")
        self.select_all.setChecked(True)
        # Show content of archive
        show_archive_layout.addWidget(self.select_all)
        show_btn = QtWidgets.QPushButton("Show")
        # Appearance
        show_btn.setMaximumWidth(50)

        show_archive_layout.addWidget(show_btn)
        # Connect
        show_btn.clicked.connect(self.show_content_of_archive)
        self.select_all.stateChanged.connect(self.select_all_status_changed)

        self.main_layout.addWidget(self.show_content_archive)

    def add_select_modules_for_update(self):
        """Select modules for update."""
        # Select modules to update
        select_modules = QtWidgets.QWidget()
        select_modules_layout = QtWidgets.QHBoxLayout(select_modules)
        # Label - description
        select_description_label = QtWidgets.QLabel("Description:")
        select_description_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.select_modules_description = QtWidgets.QTextEdit()
        self.select_modules_description.setReadOnly(True)
        # Show list of available modules updates
        select_available_label = QtWidgets.QLabel("Available:")
        select_available_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.select_modules_list = QtWidgets.QListWidget()
        self.select_modules_list.itemSelectionChanged.connect(
            self.selection_of_module_to_update_changed
        )
        self.select_modules_list.itemChanged.connect(
            self.selected_module_update_item_changed
        )
        select_modules_layout.addWidget(select_description_label)
        select_modules_layout.addWidget(self.select_modules_description)
        select_modules_layout.addWidget(select_available_label)
        select_modules_layout.addWidget(self.select_modules_list)

        self.main_layout.addWidget(select_modules)

    def add_start_update(self):
        """Start update."""
        start_udpate = QtWidgets.QWidget()
        start_update_layout = QtWidgets.QHBoxLayout(start_udpate)
        # Appearance
        start_update_layout.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight)

        update_btn = QtWidgets.QPushButton("Update")
        # Appearance
        update_btn.setMaximumWidth(60)

        start_update_layout.addWidget(update_btn)

        self.main_layout.addWidget(start_udpate)

        # Connect to logic
        update_btn.clicked.connect(self.initiate_update)

    def add_logs(self):
        """Add logs part."""
        logging_layout = QtWidgets.QVBoxLayout()
        # Test group box
        log_group_box = QtWidgets.QGroupBox("Logs")
        log_group_box.setCheckable(False)
        log_group_box.setLayout(logging_layout)
        self.main_layout.addWidget(log_group_box)

        self.logging_box = QtWidgets.QTextEdit()
        logging_layout.addWidget(self.logging_box)

    def initiate_update(self):
        """Initiate update."""
        logger.info("Update of modules started")
        for status, message in self.logic.initiate_update():
            if status and message:
                # Update ok
                logger.info(
                    "Update of module '%s' is finished.", message
                )
                # Show message to user
                self.add_log_message(
                    "Update of module '%s' is finished." % message)
            elif not status and message:
                # Fail
                logger.info("Update failed. %s", message)
                # Show message to user
                self.add_log_message(
                    "Update failed. %s" % message)
            else:
                # Global problem
                logger.warning(
                    "Global problem with update occured. Check log file.")
                # Show message to user
                self.add_log_message(
                    "Global problem with update occured. Check log file.")

        # Update finished
        message = QtWidgets.QMessageBox(self)
        message.about(
            self,
            "Update",
            "Update finished.")
        logger.info("Update finished")

    # Show content of archive
    def show_content_of_archive(self):
        """Show content of archive in simple way.

        e.g. checkbox + name of module
        """
        self.select_modules_list.clear()
        # Counter of svsilsblr moudules for update
        modules_for_update = 0

        for name, _ in self.logic.get_available_modules():
            modules_for_update += 1
            item = QtWidgets.QListWidgetItem(name)
            item.setCheckState(QtCore.Qt.CheckState.Checked)
            item.setFlags(QtCore.Qt.ItemFlag.ItemIsUserCheckable |
                          QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.select_modules_list.addItem(item)
            
        # In case anot valid, available module for update
        if modules_for_update == 0:
            message = QtWidgets.QMessageBox(self)
            message.about(
                self,
                "Error - show modules",
                "No valid module found. Check the archive content.")

    def select_all_status_changed(self):
        """Status of select all checkbox changed."""
        status = self.select_all.checkState()
        new_status = False if status == QtCore.Qt.CheckState.Unchecked\
            else True
        new_status_fe = QtCore.Qt.CheckState.Unchecked if status == \
            QtCore.Qt.CheckState.Unchecked else QtCore.Qt.CheckState.Checked
        self.select_modules_list.clear()

        for name, _ in self.logic.get_available_modules():
            self.logic.set_module_update_status(name, new_status)
            item = QtWidgets.QListWidgetItem(name)
            item.setCheckState(new_status_fe)
            item.setFlags(QtCore.Qt.ItemFlag.ItemIsUserCheckable |
                          QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.select_modules_list.addItem(item)

    def selected_module_update_item_changed(self, item):
        """Selected module item changed(checked/unchecked).

        Emitted signal over item change - checked/unchecked
        """
        # get item
        item_name = item.text()
        item_status = item.checkState()
        new_status = False
        # Ok have it
        if item_name:
            if item_status == QtCore.Qt.Checked:
                new_status = True
            self.logic.set_module_update_status(item_name, new_status)

    def selection_of_module_to_update_changed(self):
        """Selection of modules to be updated changed."""
        item = self.select_modules_list.currentItem()
        if item:
            self.show_description_for_module(item.text())

    def show_description_for_module(self, name):
        """Set description text for specified module."""
        description = "Unknown"
        if name:
            description = self.logic.get_description_for_module(name)

        self.select_modules_description.setText(description)

    def select_update_archive(self):
        """Select file/atrchove to be used for update."""
        # Clean up before start again
        self.clear_filled_form()
        dialog = QtWidgets.QFileDialog(self)
        dialog.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFile)
        archive_path, _ = dialog.getOpenFileName()

        # Process given file
        if archive_path:
            if Path(archive_path).exists():
                self.select_textbox.clear()
                self.select_textbox.insertPlainText(archive_path)
                # Process arcchive by default
                self.logic.copy_archive_to_temp_folder(archive_path)
                self.logic.process_archive(archive_path)
            else:
                message = QtWidgets.QMessageBox(self)
                message.about(
                    self,
                    "Error - select archive",
                    f"Selected archive '{archive_path}' doesn't exist.")

    def clear_filled_form(self):
        """Clear all filled boxes, etc."""
        self.select_textbox.clear()
        self.select_modules_list.clear()

    def add_log_message(self, message):
        """Add log message + timestamp.

        Args:
        message = just simple logg message(be processed ass str)
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        full_message = "%s - %s" % (
            timestamp,
            message)
        self.logging_box.append(full_message)
