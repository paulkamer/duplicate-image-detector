import imghdr
import logging
import os
import re
import shutil
from pathlib import Path
from .detectors import SiftDuplicateDetector


def app(**options: dict):
    if (options.get('restore')):
        _restore_duplicates(options.get('config'))

    images = _load_images(options.get('config'))

    duplicates = SiftDuplicateDetector(
        images, **options).determine_duplicates()

    if (duplicates):
        logging.info(f"Total duplicates found: {len(duplicates)}")

        for key in duplicates:
            logging.info(key)
            for duplicate in duplicates[key]:
                logging.info(
                    f"\t- {duplicate} - {len(duplicates[key][duplicate]['matches'])} matched descriptors")

        logging.info(f"Moving duplicates")
        _move_duplicates(options.get('config'), duplicates.keys())


def _load_images(config: dict) -> list:
    images = []

    filepath_ignore_regex = re.compile(r'\.gitkeep')

    for file in Path(config['paths']['images_dir']).iterdir():
        if not file.is_file():
            continue

        path = file.as_posix()

        if re.search(filepath_ignore_regex, path):
            continue

        # Check if it's a supported image
        filetype = imghdr.what(path)
        logging.debug(f"{path} - {filetype}")
        if (filetype not in config['files']['supported_image_types'].split(',')):
            logging.info('Unsupported file type: ' + str(filetype))
            continue

        images.append(path)

    return images


def _move_duplicates(config: dict, duplicates: list) -> None:
    """
    Move images detected as duplicate to a separate dir

    Parameters
    ----------
    duplicates : list
        Duplicate images that should be moved to the duplicates dir
    """
    os.makedirs(config['paths']['duplicates_dir'], exist_ok=True)

    for duplicate in duplicates:
        shutil.move(os.path.join(config['paths']['images_dir'], duplicate),
                    os.path.join(config['paths']['duplicates_dir'], duplicate))


def _restore_duplicates(config: dict):
    """
    Move duplicates back to the images dir
    """
    if (not os.path.isdir(config['paths']['duplicates_dir'])):
        return

    for file in Path(config['paths']['duplicates_dir']).iterdir():
        if not file.is_file():
            continue

        path = file.as_posix()
        shutil.move(path, os.path.join(
            config['paths']['images_dir'], os.path.basename(path)))
