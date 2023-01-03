import imghdr
import logging
import os
import re
import shutil
from pathlib import Path
from .detectors import SiftDuplicateDetector


def app(**options: dict):
    __init_logger(options)
    config = options.get('config')

    options.get('restore') and __restore_duplicates(config)

    new_images = __load_images(config['paths']['new_images_dir'], config)
    existing_images = __load_images(config['paths']['images_dir'], config)

    duplicates = SiftDuplicateDetector(
        new_images, existing_images, **options).detect()
    logging.info(f"# duplicates found: {len(duplicates)}")

    if (duplicates):
        __log_duplicates(duplicates)

        if (options.get('remove')):
            __delete_duplicates(config, duplicates.keys())
        else:
            __move_duplicates(config, duplicates.keys())

    __store_new_unique_images(config)


def __init_logger(options: dict):
    log_level = logging.DEBUG if options['debug'] == True else logging.WARN

    logging.basicConfig(level=log_level)

    logging.info(
        f"Logger initialized in mode {logging.getLevelName(log_level)}")


def __load_images(folder: str, config: dict) -> list:
    images = []

    filepath_ignore_regex = re.compile(r'\.gitkeep')
    for file in Path(folder).iterdir():
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


def __log_duplicates(duplicates):
    for key in duplicates:
        logging.info(key)
        for duplicate in duplicates[key]:
            logging.info(
                f"\t- {duplicate} - {len(duplicates[key][duplicate]['matches'])} matched descriptors")


def __move_duplicates(config: dict, duplicates: list) -> None:
    """
    Move images detected as duplicate to a separate dir

    Parameters
    ----------
    duplicates : list
        Duplicate images that should be moved to the duplicates dir
    """
    logging.info(f"Moving duplicates")

    os.makedirs(config['paths']['duplicates_dir'], exist_ok=True)

    for duplicate in duplicates:
        shutil.move(os.path.join(config['paths']['new_images_dir'], duplicate),
                    os.path.join(config['paths']['duplicates_dir'], duplicate))


def __delete_duplicates(config: dict, duplicates: list) -> None:
    """
    Delete new images detected as a duplicate
    """
    for duplicate in duplicates:
        os.remove(os.path.join(config['paths']['new_images_dir'], duplicate))


def __store_new_unique_images(config: dict) -> None:
    """
    Move new unique images to the root images dir
    """
    target_dir = config['paths']['images_dir']
    for file in Path(config['paths']['new_images_dir']).iterdir():
        if not file.is_file():
            continue

        path = file.as_posix()
        shutil.move(path, os.path.join(target_dir, os.path.basename(path)))


def __restore_duplicates(config: dict):
    """
    Move duplicates back to the new images dir
    """
    if (not os.path.isdir(config['paths']['duplicates_dir'])):
        return

    target_dir = config['paths']['new_images_dir']
    for file in Path(config['paths']['duplicates_dir']).iterdir():
        if not file.is_file():
            continue

        path = file.as_posix()
        shutil.move(path, os.path.join(target_dir, os.path.basename(path)))
