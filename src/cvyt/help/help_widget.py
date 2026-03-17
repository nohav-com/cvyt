"""Help for the window/widget."""
import logging

from PySide6 import QtPdf, QtPdfWidgets, QtWidgets

from cvyt.help.help_logic import HelpLogic

__all__ = ['CreateHelpWindow']


logger = logging.getLogger(__name__)


class CreateHelpWindow(QtWidgets.QWidget):
    """Creating the help window to display the help content."""

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.logic = HelpLogic(**kwargs)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.main_layout)

        self.add_title()
        self.add_pdf_view()
        # Collect info from the config file
        self.logic.get_info_from_config()

    def get_use_browser(self) -> bool:
        """Get the flag indicating whether a web browser is being used."""
        return self.logic.get_use_browser()

    def get_help_path(self) -> str | None:
        """Get the path of the help file."""
        return self.logic.get_help_path()

    def show_pdf_file(self):
        """Show the content of the pdf file."""
        help_path = self.get_help_path()
        if help_path:
            self.pdf.load(help_path)
        else:
            logger.error("No path to the help file found.")

    def add_title(self, title='Help'):
        """Add the title of the widget."""
        self.setWindowTitle(title)

    def add_pdf_view(self):
        """Add the pdf view to the widget."""
        self.pdf = QtPdf.QPdfDocument()
        self.pdf_view = QtPdfWidgets.QPdfView()
        # Set that we are expecting multipage pdf
        self.pdf_view.setPageMode(
            QtPdfWidgets.QPdfView.PageMode.MultiPage)
        # Set to fit the widget(width)
        self.pdf_view.setZoomMode(
            QtPdfWidgets.QPdfView.ZoomMode.FitToWidth
        )
        self.pdf_view.setDocument(self.pdf)
        self.main_layout.addWidget(self.pdf_view)
