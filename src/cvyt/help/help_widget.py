"""Help window/widget."""
import logging

from PySide6 import QtPdf, QtPdfWidgets, QtWidgets

from cvyt.help.help_logic import HelpLogic

__all__ = ['CreateHelpWindow']


logger = logging.getLogger(__name__)


class CreateHelpWindow(QtWidgets.QWidget):
    """Creating help window for presenting help content."""

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.logic = HelpLogic(**kwargs)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.main_layout)

        self.add_title()
        self.add_pdf_view()
        # Gather infor from config if available
        self.logic.get_info_from_config()

    def get_use_browser(self) -> bool:
        """Get flag if we are using web browser."""
        return self.logic.get_use_browser()

    def get_help_path(self) -> str | None:
        """Get path to help file."""
        return self.logic.get_help_path()

    def show_pdf_file(self):
        """Show content of pdf file."""
        help_path = self.get_help_path()
        if help_path:
            self.pdf.load(help_path)
        else:
            logger.error("No path to help file founded.")

    def add_title(self, title='Help'):
        """Add title to widget."""
        self.setWindowTitle(title)

    def add_pdf_view(self):
        """Add pdf view to the widget."""
        self.pdf = QtPdf.QPdfDocument()
        self.pdf_view = QtPdfWidgets.QPdfView()
        # Set we are expecting multipage pdf
        self.pdf_view.setPageMode(
            QtPdfWidgets.QPdfView.PageMode.MultiPage)
        # Set to fit the widget(width)
        self.pdf_view.setZoomMode(
            QtPdfWidgets.QPdfView.ZoomMode.FitToWidth
        )
        self.pdf_view.setDocument(self.pdf)
        self.main_layout.addWidget(self.pdf_view)
