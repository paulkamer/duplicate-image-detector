import os
import imghdr
import logging
import shutil
import re
from pathlib import Path


def load_images(images_dir: str, config: dict) -> list:
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
        if (filetype not in config['files']['supported_image_types'].split(',')):
            logging.info('Unsupported file type: ' + str(filetype))
            continue

        images.append(path)

    return images


def move_duplicates(config: dict, duplicates: list) -> None:
    """
    Move images detected as duplicate to a separate dir

    Parameters
    ----------
    duplicates : list
        Duplicate images that should be moved to the duplicates dir
    """
    logging.debug(f"Moving duplicates")

    os.makedirs(config['paths']['duplicates_dir'], exist_ok=True)

    for duplicate in duplicates:
        __move_file(duplicate, config['paths']['duplicates_dir'])


def delete_duplicates(config: dict, duplicates: list) -> None:
    """
    Delete new images detected as a duplicate
    """
    logging.debug(f"Deleting duplicates")

    for duplicate in duplicates:
        os.remove(duplicate)


def store_new_unique_images(config: dict) -> None:
    """
    Move new unique images to the root images dir
    """
    logging.debug(f"Storing new unique images")

    __move_all_files(config['paths']['new_images_dir'], config['paths']['images_dir'])


def restore_duplicates(config: dict):
    """
    Move duplicates back to the new images dir
    """
    logging.debug(f"Restoring duplicates")

    __move_all_files(config['paths']['duplicates_dir'], config['paths']['new_images_dir'])


def __move_all_files(source_dir: str, target_dir: str):
    if (not os.path.isdir(source_dir) or not os.path.isdir(target_dir)):
        return

    for file in Path(source_dir).iterdir():
        if not file.is_file():
            continue

        __move_file(file.as_posix(), target_dir)


def __move_file(fullpath, target_dir):
    shutil.move(fullpath, os.path.join(target_dir, os.path.basename(fullpath)))
