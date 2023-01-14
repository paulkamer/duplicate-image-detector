import logging

from .db import DbHandler
from .fileshelper import FilesHelper
from .imageloader import ImageLoader
from .detectors import SiftDuplicateDetector
from .duplicateshandler import DuplicatesHandler
from .new_unique_images_handler import NewUniqueImagesHandler


def app(**options: dict):
    init_logger(options.get('debug'))

    config = options.get('config')
    dbhandler = DbHandler(config)
    fileshelper = FilesHelper(config)

    options.get('restore_duplicates') and fileshelper.restore_duplicates()

    new_images, existing_images = ImageLoader(fileshelper, config).load_images()
    images = {
        'new': new_images,
        'existing': existing_images
    }

    detector = SiftDuplicateDetector(images, options)
    duplicates = detector.detect()

    DuplicatesHandler(fileshelper, options).handle(duplicates)

    new_unique_images = [image for image in new_images if image not in duplicates]
    if (new_unique_images):
        NewUniqueImagesHandler(fileshelper, dbhandler, config).handle(new_unique_images, detector.get_computed_images())


def init_logger(debug: bool):
    log_level = logging.DEBUG if debug == True else logging.INFO

    logging.basicConfig(level=log_level)
    logging.debug(f"Logger initialized in mode {logging.getLevelName(log_level)}")
