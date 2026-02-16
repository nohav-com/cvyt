# -*- coding: utf-8 -*-
"""Logic for update widget."""

import logging
import os
import shutil
import tarfile
import zipfile
from pathlib import Path

from cvyt.common_update import CommonUpdate

__all__ = ['UpdateLogic']

logger = logging.getLogger(__name__)


class UpdateLogic():
    """Update logic supporting updare widnow/widget."""
    def __init__(self, /, **kwargs):
        self.config = kwargs.get('config', None)
        self.common_update = CommonUpdate(**kwargs)
        self.temp_folder = kwargs.get(
            "temp_update", self.common_update.get_temp_folder_name())

    def process_archive(self, archive: str, to_folder: str = None):
        """Unpack given archive.

        Args:
        archive = path to archive
        to_folder = optional path to folder where to extrack archive
        """

        if to_folder:
            self.temp_folder = to_folder
        try:
            if zipfile.is_zipfile(archive):
                # Unzip archive
                zip_file = zipfile.ZipFile(archive)
                zip_file.extractall(self.temp_folder)
            elif tarfile.is_tarfile(archive):
                with tarfile.open(archive) as file_in:
                    file_in.extractall(self.temp_folder)
            else:
                logger.info("Unknown format of archive '%s'.", archive)
        except Exception as e:
            logger.error(
                "Processing or archive '%s' failed(%s).",
                archive,
                e)
        self.common_update.create_update_list(self.temp_folder)

    def initiate_update(self):
        """Update specific part."""
        try:
            # Lets try update each module from archive
            modules_root = self.common_update.get_modules_root_path()
            if not Path(modules_root).exists():
                Path(modules_root).mkdir()
            for name, module in self.common_update.get_available_modules():
                # We should update this module
                if module.get('update', None):
                    dst_path = (Path(modules_root).joinpath(name))
                    # Check if main folder exists
                    if not dst_path.exists():
                        dst_path.mkdir()
                    root = module.get('root', None)
                    if root:
                        try:
                            # Copy
                            shutil.copytree(
                                str(root),
                                str(dst_path),
                                dirs_exist_ok=True
                            )

                            yield (True, name)
                        except Exception as e:
                            logger.warning(
                                """Could not finish update of item
                                      '%s' because %s.""", name, e
                            )
                            message = """Could not finish update of item
                                      '%s' because %s.""" % (name, e)
                            yield (False, message)
                    else:
                        logger.warning(
                            "Not 'root' folder found for '%s'.", name)
                        message = """Not 'root' folder found for '%s'.""" %\
                                  name
                        yield (False, message)
        except Exception as e:
            error_message = f"{e}"
            yield (False, error_message)

    def get_available_modules(self):
        """Get available module.

        Returns:
        tuple with (name, module object)
        """
        return self.common_update.get_available_modules()

    def get_description_for_module(self, name: str) -> str | None:
        """Get description for selected module.

        Args:
        name = name of the module

        Returns:
        Description or None
        """
        description = None
        if name:
            description = self.common_update.get_value_for_key(
                name, "description")
        return description

    def set_module_update_status(self, module_name: str, status: bool):
        """Set status to module.

        Args:
        module_name = name of the module
        status = status to set
        """
        if module_name and status is not None:
            self.common_update.set_value_for_key(
                module_name, "update", status)

    def copy_archive_to_temp_folder(self, archive: str):
        """Copy archive from original location to temp folder.

        Args:
        archive = path to archive to remove
        """
        self.create_temp_folders()
        if archive and Path(archive).exists():
            shutil.copy(archive, self.temp_folder)

    def remove_archive(self, archive: str):
        """Remove archive from temp folder.

        Args:
        archive = path to archive to remove
        """
        if Path(archive).exists():
            os.unlink(archive)

    def create_temp_folders(self):
        """Create temp folder."""
        if Path(self.temp_folder).exists():
            shutil.rmtree(self.temp_folder, ignore_errors=True)
        # Just try to create it
        Path(self.temp_folder).mkdir(exist_ok=True)
