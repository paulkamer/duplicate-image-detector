import logging
from pathlib import Path

from . import fileshelper
from .detectors import SiftDuplicateDetector


def app(**options: dict):
    config = options.get('config')
    init_logger(options.get('debug'))

    options.get('restore') and fileshelper.restore_duplicates(config)

    new_images, existing_images = load_images(config)

    duplicates = SiftDuplicateDetector(new_images,
                                       existing_images,
                                       options.get('config')['sift'],
                                       options.get('render_comparison_images')
                                       ).detect()

    handle_duplicates(duplicates, config, options.get('remove'))

    handle_new_unique_images(new_images, duplicates, config)


def init_logger(debug: bool):
    log_level = logging.DEBUG if debug == True else logging.INFO

    logging.basicConfig(level=log_level)
    logging.debug(f"Logger initialized in mode {logging.getLevelName(log_level)}")


def load_images(config):
    new_images = fileshelper.load_images(config['paths']['new_images_dir'], config)
    existing_images = fileshelper.load_images(config['paths']['images_dir'], config)

    return new_images, existing_images


def handle_duplicates(duplicates, config, remove_duplicates: bool):
    logging.info(f"Duplicates found: {len(duplicates)}")

    if (duplicates):
        log_duplicates(duplicates)

        if (remove_duplicates):
            fileshelper.delete_duplicates(config, duplicates.keys())
        else:
            fileshelper.move_duplicates(config, duplicates.keys())


def handle_new_unique_images(new_images, duplicates, config):
    if (len(new_images) > len(duplicates)):
        fileshelper.store_new_unique_images(config)


def log_duplicates(duplicates):
    for key in duplicates:
        logging.info(key)
        for duplicate in duplicates[key]:
            logging.info(
                f"\t- {duplicate} - {len(duplicates[key][duplicate]['matches'])} matched descriptors")
