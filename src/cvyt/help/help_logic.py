"""Logic for the help window/widget."""
from pathlib import Path
import logging

# Help tag
HELP_INFO = ["help"]

__all__ = ['HelpLogic']


logger = logging.getLogger(__name__)


class HelpLogic():
    """Basic logic for the help widget."""
    def __init__(self, **kwargs):
        self.config = kwargs.get("config", None)
        self.help_path = None
        self.cwd = kwargs.get("cwd", None)
        # Are we using browser - default
        self.browser = True

    def get_info_from_config(self):
        """Return the name of the help file."""
        if self.config:
            help_info = self.config.get_value_for_key(HELP_INFO)
            if help_info and self.cwd:
                help_file_name = help_info.get("file", None)
                self.help_path = Path(self.cwd).joinpath(help_file_name)\
                    if help_file_name else None
                self.browser = help_info.get("browser", None)

    def get_use_browser(self) -> bool:
        """Get the flag indicating whether we are using a web browser."""
        return self.browser

    def get_help_path(self) -> str | None:
        """Return the path to the help file."""
        return str(self.help_path) if self.help_path else None
