# -*- coding: utf-8 -*-
"""Main entry point to cvyp app."""

import logging
import sys
import webbrowser
from pathlib import Path

from PySide6 import QtCore, QtGui, QtWidgets

from cvyt.config.config_widget import CreateConfigWindow as ConfigWindow
from cvyt.config_logic import ConfigLogic
from cvyt.cvyt_logic import CvytLogic
from cvyt.help.help_widget import CreateHelpWindow as HelpWindow
from cvyt.info.info_widget import CreateInfoWindow as InfoWindow
from cvyt.logging_settings import set_logging_settings
from cvyt.modules_available_logic import ModelAvailableModules
from cvyt.update.update_widget import CreateUpdateWindow as UpdateWindow

__all__ = ['Show']

# Default resolution 4K --> move it to settings json file
X_4K: int = 3840
Y_4K: int = 2160

# Bulgarians coefficients for left overview menu
X_COEFFICIENT = 0.11
Y_COEFFICIENT = 0.2

logger = logging.getLogger(__name__)


class Show():
    """Show main window/widget of cvyt app."""
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)

    def show(self):
        # Create main widget
        self.main_window = CreateMainWindow()
        # Get all available screens
        all_screens = QtWidgets.QApplication.screens()
        # Set default resolution
        x: int = X_4K
        y: int = Y_4K
        # In case only 1 screen available
        if len(all_screens) == 1:
            # Get its resolution
            x, y = all_screens[0].size().toTuple()
        # Apply resolution
        self.main_window.resize(x, y)
        self.main_window.set_size_xy(x, y)
        # Show the main widget
        self.main_window.show()

        self.main_window.valid_config_status()

        self.close()

    def close(self):
        """Kill the app"""

        sys.exit(self.app.exec())

    def closeEvent(self, event):
        sys.exit(self.app.exec())
        self.main_window.close()


class CreateMainWindow(QtWidgets.QMainWindow):
    """Creating main window of app cvyt."""

    def __init__(self):
        super().__init__()
        self.cvyt_logic = CvytLogic()

        # Variables
        self.available_modules = []
        self.size_x = X_4K
        self.size_y = Y_4K
        self.available_modules_model = None
        self.available_modules = None
        self.app_config = None
        # Magic tab counter --> no name -->add id of tab
        self.tabs_counter = 0
        # Widgets
        self.left_overview = None
        self.tabs_widget = None
        self.description_text = None
        # Set logging settings
        set_logging_settings()
        # Load config file and store it config object
        self.load_object_related_to_app_config()
        # Get resolution form config file
        self.x, self.y = self.app_config.get_resolution()

        # Create main window
        self.add_title()
        self.add_menu_bar()
        self.add_cental_widget()

    def add_title(self, title=None):
        """Add title of the main window.

        Args:
        title = specified title
        """
        if title:
            # Add title to window/widget
            self.setWindowTitle(title)
        else:
            # Title from config file
            self.setWindowTitle(self.app_config.get_title())

    def add_menu_bar(self):
        """"Add menu."""
        # Menu --> exit
        self.main_item = self.menuBar().addMenu("&Main")
        self.exit_action = QtGui.QAction("&Exit", self)
        self.main_item.addAction(self.exit_action)
        # Option for updatw widget
        self.update_action = QtGui.QAction("&Update", self)
        self.menuBar().addAction(self.update_action)
        # Option for config widget
        self.config_action = QtGui.QAction("&Config", self)
        self.menuBar().addAction(self.config_action)
        # Info widget
        self.info_action = QtGui.QAction("&Info", self)
        self.menuBar().addAction(self.info_action)
        # help widget
        self.help_action = QtGui.QAction("&Help", self)
        self.menuBar().addAction(self.help_action)
        # Connect to methods handling each option
        self.help_action.triggered.connect(self.open_help_widget)
        self.exit_action.triggered.connect(self.close_app)
        self.config_action.triggered.connect(self.open_app_config_widget)
        self.update_action.triggered.connect(self.update_widget)
        self.info_action.triggered.connect(self.info_widget)

    def valid_config_status(self):
        """Check if config object is processed and set."""
        if not self.app_config:
            logger.error("Problem with loading app_config.json.",
                         "Its propably not valid json file."
                         "Check its content.")
            message = QtWidgets.QMessageBox(self)
            message.about(
                self,
                "Error - load config",
                """Problem with loading app_config.json.
                Its propably not valid json file.
                Check its content.""")

    def load_object_related_to_app_config(self):
        """Load all object related to app_config."""
        # Create main app config object + handler
        self.app_config = ConfigLogic()

        # Capable to get config object
        if self.app_config.get_config_object():
            try:
                # Prepare logic for processing available modules
                self.available_modules_model = ModelAvailableModules(
                    config=self.app_config
                )
                # Get available modules
                self.get_available_modules()
            except Exception as e:
                # Problem
                logger.error("Could not load app config file(%s),", e)
                self.app_config = None
        else:
            # Some problem
            self.app_config = None
            logger.error("App config object does not exists.")

    def get_available_modules(self):
        """Get all available modules(process folder, validation)."""
        self.available_modules_model.create_modules_list()

    def closeEvent(self, event):
        """Close the app, event reaction."""
        self.close_app()

    def close_app(self):
        """Close the app."""
        self.close()

    def set_size_xy(self, x: int, y: int):
        """Set size of the window.

        Args:
        x = x-axis
        y = y-axis
        """
        self.size_x = x
        self.size_y = y

    def widget_already_in_tabs_list(self, widget: str) -> int:
        """Check if tab/window with specified name is already present
        int the list of tabs.

        Args:
        widget = name of the widget/tab

        Returns:
        index of the widget/tab otherwise -1 for not existing
        """
        index_of_tab: int = -1
        # Check each tab
        for index in range(self.tabs_widget.count()):
            if self.tabs_widget.tabWhatsThis(index).lower() == widget.lower():
                index_of_tab = index
                break

        return index_of_tab

    def current_count_of_tabs(self) -> int:
        """Get current count of opened tabs."""
        return (0 if self.tabs_widget.count() - 1 < 0
                else self.tabs_widget.count() - 1)

    @QtCore.Slot()
    def update_widget(self):
        # Default name of the tab
        widget_name = "Update"
        # Check if widget of this type is already opened
        index = self.widget_already_in_tabs_list(widget_name)
        # Not --> lets prepare it
        if index == -1:
            # Reload config object
            self.app_config.reload_config()
            # Create update window/tab
            self.create_tab = UpdateWindow(config=self.app_config)
            # Add it to tab widget
            self.tabs_widget.addTab(self.create_tab, widget_name)
            self.tabs_widget.setTabWhatsThis(
                self.tabs_widget.count() - 1, widget_name)
            # Focus on new tab
            self.tabs_widget.setCurrentIndex(self.current_count_of_tabs())
        else:
            # Existing --> set focus on it
            self.tabs_widget.setCurrentIndex(index)

    @QtCore.Slot()
    def info_widget(self):
        """Prepare and open info widget."""
        widget_name = "Info"
        # Check if info window/tab is already opened.
        index = self.widget_already_in_tabs_list(widget_name)
        # Not --> lets prepare it
        if index == -1:
            # Reload config object
            self.app_config.reload_config()
            # Create info window
            self.info_tab = InfoWindow(
                config=self.app_config)
            # Add it to tab widget
            self.tabs_widget.addTab(self.info_tab, widget_name)
            self.tabs_widget.setTabWhatsThis(
                self.tabs_widget.count() - 1, widget_name)
            # Focus on the new tab
            self.tabs_widget.setCurrentIndex(self.current_count_of_tabs())
        else:
            # Existing --> set focus on it
            self.tabs_widget.setCurrentIndex(index)

    @QtCore.Slot()
    def open_app_config_widget(self):
        """Prepare and open config file(app's config file).

        This method should be used only to open app config, not config file
        from outside.
        """
        # Config object exists.
        if self.app_config:
            # Reload content of config object to reflect new changes
            # self.app_config.reload_config()
            self.app_config.load_config()
            # Open it
            self.config_tab(self.app_config, name="Config - cvyt")

    def open_config_widget(self, config_path: str, name: str = None):
        """Global method helps to open config window/widget.

        Can be used ifrom different module to open its config file.

        Args:
        config_path = path(absolute) to config file to be opened
        name = name of the config widget, default None-->needs to be created
        """
        tab_name = name
        if not name:
            tab_name = f"Config - {self.tabs_counter}"
            self.tabs_counter += 1

        if Path(config_path).exists():
            # Config file exists --> lets prepare it
            config = ConfigLogic(config=config_path)
            if config:
                try:
                    # already openning it in new tab
                    self.config_tab(config, tab_name)
                except Exception as e:
                    # We have problem
                    logger.error("Attemp to open oconfig tab failed(%s).", e)
            else:
                message = QtWidgets.QMessageBox(self)
                message.about(
                    self,
                    "Error - open config widget",
                    f"Config file '{config_path}' doesnt have valid format.")
        else:
            message = QtWidgets.QMessageBox(self)
            message.about(
                self,
                "Error - open config widget",
                f"Config file doesnt exist '{config_path}'.")

    def config_tab(self, config: ConfigLogic, name: str):
        """Open custom config widget.

        Args:
        config = config object
        name = name of the tab where config will be opened
        """
        # Tab already opened?
        index = self.widget_already_in_tabs_list(name)
        if index == -1:
            # Not, lets prepare it and pin it.
            config_tab = ConfigWindow(config=config)
            self.tabs_widget.addTab(config_tab, name)
            self.tabs_widget.setTabWhatsThis(
                self.tabs_widget.count() - 1, name)

            # Focus on new tab
            self.tabs_widget.setCurrentIndex(self.current_count_of_tabs())
        else:
            # Existing --> set focus on it
            self.tabs_widget.setCurrentIndex(index)

    def open_help_widget_browser(self, help_path: str):
        """Open help via webbrowser. Global use(external modules).

        Args:
        help_path = full path to help file
        """
        try:
            if help_path:
                # Just open it
                webbrowser.open(str(help_path), new=1)
            else:
                # Something is wrong
                message = QtWidgets.QMessageBox(self)
                message.about(
                    self,
                    "Error - open help widget",
                    ("Cannot open hel pfile '%s' not filled.", help_path))
        except Exception as e:
            message = QtWidgets.QMessageBox(self)
            message.about(
                self,
                "Error - open help widget",
                ("Cannot open hel pfile '%s' because %s", help_path, e))

    @QtCore.Slot()
    def open_help_widget(self):
        """Open help widget or eventually browser. Internal use."""
        name = "Help"
        # Update config(reload)
        self.app_config.reload_config()
        index = self.widget_already_in_tabs_list(name)
        if index == -1:
            # Prepare the help window
            help = HelpWindow(
                config=self.app_config,
                cwd=str(Path(__file__).cwd()))
            # Get if we are going with webbrowser or not
            browser = help.get_use_browser()

            # Not browser, so tab
            if not browser:
                # Pin it to tabs
                help.show_pdf_file()
                self.tabs_widget.addTab(
                    help, name)
                self.tabs_widget.setTabWhatsThis(
                        self.tabs_widget.count() - 1, name)
                self.tabs_widget.setCurrentIndex(self.current_count_of_tabs())
            elif browser:
                # Go with browser
                self.open_help_widget_browser(help.get_help_path())
            else:
                message = QtWidgets.QMessageBox(self)
                message.about(
                    self,
                    "Error - open help widget",
                    "No help file available")
        else:
            # Existing --> set focus on it
            self.tabs_widget.setCurrentIndex(index)

    def add_left_overview_menu(self):
        """Add left overview menu."""
        # Left side overview
        self.left_overview = QtWidgets.QWidget()
        # Calculate maximaze size of left overview
        self.left_overview.setMaximumSize(self.max_size_left_overview())
        left_overview_layout = QtWidgets.QVBoxLayout(self.left_overview)
        # Modules label
        modules_label = QtWidgets.QLabel("Available modules:")
        # Add to main left layout
        left_overview_layout.addWidget(modules_label)
        # List of modules)
        self.list_of_modules = QtWidgets.QListView()
        self.list_of_modules.setModel(self.available_modules_model)
        # Add to main layout
        left_overview_layout.addWidget(self.list_of_modules)
        # Connect to method
        available_modules_selection = \
            self.list_of_modules.selectionModel()
        available_modules_selection.selectionChanged.connect(
            self.available_module_selected)
        self.list_of_modules.doubleClicked.connect(self.open_module_tab)
        # Open module in new tab
        module_open_btn = QtWidgets.QPushButton("Open")
        # Appearance limitation
        module_open_btn.setMaximumWidth(50)
        left_overview_layout.addWidget(module_open_btn)
        # Description of selected module
        description_label = QtWidgets.QLabel("Description:")
        self.description_text = QtWidgets.QLabel()
        left_overview_layout.addWidget(description_label)
        left_overview_layout.addWidget(self.description_text)
        # Connect method
        module_open_btn.clicked.connect(self.open_module_tab)

    @QtCore.Slot()
    def add_cental_widget(self):
        """Central widget wrapping everything."""
        # Parent widget
        parent_widget = QtWidgets.QWidget()
        # Grid layout - parent widget
        parent_grid_layout = QtWidgets.QGridLayout(parent_widget)
        self.add_left_overview_menu()
        # Right Tabs widget
        right_tabs = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_tabs)
        # Create right tabs widget
        self.tabs_widget = QtWidgets.QTabWidget()
        right_layout.addWidget(self.tabs_widget)
        right_tabs.setLayout(right_layout)
        # Settings of tab widget
        self.tabs_widget.setTabsClosable(True)
        self.tabs_widget.setMovable(True)
        # Connect to specific method
        self.tabs_widget.tabCloseRequested.connect(self.close_tab)

        # Add widgets to parent widget
        parent_grid_layout.addWidget(self.left_overview, 0, 0)
        parent_grid_layout.addWidget(right_tabs, 0, 1)

        # Set default widget to the main window
        self.setCentralWidget(parent_widget)

        # Add default info tab to tab widget
        self.info_widget()

    def open_module_tab(self):
        """Open selected module in new tab or switch focus at already existing
        tab with this module."""
        # Get index of selected module
        indexes = self.list_of_modules.selectedIndexes()
        # Ok, we have some module
        if indexes and len(indexes) == 1:
            # Get name of that module(tab)
            name = self.available_modules_model.get_name_of_module(
                indexes[0].row()
            )
            # Is that module already opened it tab?
            index = self.widget_already_in_tabs_list(name) if name else -1

            # It is not, let open it
            if index == -1 and name:
                # Get rest of the info about module
                module_info = self.available_modules_model.get_module_info(
                    name)
                # import module
                module = self.cvyt_logic.import_module(
                    name, module_info, self, self.app_config)

                if module:
                    # Pin this module to to tab list
                    self.tabs_widget.addTab(module, name)
                    self.tabs_widget.setTabWhatsThis(
                        self.tabs_widget.count() - 1, name)
                    self.tabs_widget.setCurrentIndex(
                        self.current_count_of_tabs())
                else:
                    # Selected nothing
                    message = QtWidgets.QMessageBox(self)
                    message.about(
                        self,
                        "Error - open module tab",
                        f"Import of module '{name}' failed. Check log file.")
            else:
                # Existing --> set focus at this tab
                self.tabs_widget.setCurrentIndex(index)
        else:
            # Selected nothing
            message = QtWidgets.QMessageBox(self)
            message.about(
                self,
                "Error - open module tab",
                "No module selected")

    def available_module_selected(self):
        """Get selected module form list of available modules."""
        # Module selected
        indexes = self.list_of_modules.selectedIndexes()
        if indexes and len(indexes) == 1:
            # Get name of the module
            name = self.available_modules_model.get_name_of_module(
                indexes[0].row()
            )
            # Get desctription for module
            description = self.available_modules_model.\
                get_value_for_key_in_module(name, "description")
            # Set description
            self.set_description_text(description)

    def set_description_text(self, description: str):
        """Set/show description for selected module."""
        if description:
            self.description_text.setText(description)

    def close_tab(self, index: int):
        """Close the tab with specific index.

        Args:
        index = index of the tab to close        
        """
        self.tabs_widget.removeTab(index)
        # Count of all available widgets --> if equal 0
        # --> show info tab
        if self.tabs_widget.count() == 0:
            self.info_widget()

    def max_size_left_overview(self):
        # Maximum size of the left overview menu
        # Using bulgarian's constant :)
        return QtCore.QSize(
            self.size_x * X_COEFFICIENT, self.size_y * Y_COEFFICIENT)


if __name__ == "__main__":
    rc = 1
    try:
        # Get main widget
        widget = Show()
        widget.show()
        rc = 0
    except Exception as e:
        logger.error("Everything went to hell %s", e)
        sys.exit(rc)
