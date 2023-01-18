import os
import imghdr
import logging
import shutil
import re
from pathlib import Path


class FilesHelper:
    def __init__(self, config: dict):
        self.config = config

    def load_images(self, images_dir: str) -> list:
        images = []

        filepath_ignore_regex = re.compile(r'\.gitkeep')
        for file in Path(images_dir).iterdir():
            if not file.is_file():
                continue

            path = file.as_posix()

            if re.search(filepath_ignore_regex, path):
                continue

            # Check if it's a supported image
            filetype = imghdr.what(path)
            logging.debug(f"{path} - {filetype}")
            if (filetype not in self.config['files']['supported_image_types'].split(',')):
                logging.info('Unsupported file type: ' + str(filetype))
                continue

            images.append(path)

        return images

    def move_duplicates(self, files: list) -> None:
        """
        Move images detected as duplicate to a separate dir

        Parameters
        ----------
        duplicates : list
            Duplicate images that should be moved to the duplicates dir
        """
        logging.debug(f"Moving duplicates")

        os.makedirs(self.config['paths']['duplicates_dir'], exist_ok=True)

        for file in files:
            self._move_file(file, self.config['paths']['duplicates_dir'])

    def delete_duplicates(self, files: list) -> None:
        """
        Delete new images detected as a duplicate
        """
        logging.debug(f"Deleting duplicates")

        for file in files:
            os.remove(file)

    def store_new_image(self, file: str) -> None:
        """
        Move new unique images to the root images dir
        """
        self._move_file(file, self.config['paths']['images_dir'])

    def restore_duplicates(self):
        """
        Move duplicates back to the new images dir
        """
        logging.debug(f"Restoring duplicates")

        self._move_all_files(self.config['paths']['duplicates_dir'], self.config['paths']['new_images_dir'])

    def _move_all_files(self, source_dir: str, target_dir: str):
        if (not self._check_dir(source_dir) or not self._check_dir(target_dir)):
            logging.warn(
                f"Moving files from {source_dir} to {target_dir} failed. One of the directories does not exist")
            return

        for file in Path(source_dir).iterdir():
            if not file.is_file():
                continue

            self._move_file(file.as_posix(), target_dir)

    def _check_dir(self, directory: str):
        return os.path.isdir(directory)

    def _move_file(self, fullpath: str, target_dir: str):
        shutil.move(fullpath, os.path.join(target_dir, os.path.basename(fullpath)))
