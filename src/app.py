import logging

from .db import DbHandler
from .fileshelper import FilesHelper
from .imageloader import ImageLoader
from .image_mapper import ImageMapper
from .detectors import SiftDuplicateDetector
from .duplicateshandler import DuplicatesHandler
from .new_unique_images_handler import NewUniqueImagesHandler


def app(**options: dict):
    init_logger(options.get('debug'))

    config = options.get('config')
    dbhandler = DbHandler(config)
    fileshelper = FilesHelper(config)
    imagemapper = ImageMapper()

    options.get('restore_duplicates') and fileshelper.restore_duplicates()

    images = _load_images(fileshelper, dbhandler, imagemapper, config)

    detector = SiftDuplicateDetector(images, options)
    detector.detect()

    duplicates = detector.get_duplicates()
    computed_images = detector.get_computed_images()

    DuplicatesHandler(fileshelper, options).handle(duplicates)

    new_unique_images = [image for image in images['new'] if image.filename not in duplicates]
    if (new_unique_images):
        NewUniqueImagesHandler(fileshelper, imagemapper, dbhandler).handle(new_unique_images, computed_images)


def init_logger(debug: bool):
    log_level = logging.DEBUG if debug == True else logging.INFO

    logging.basicConfig(level=log_level)
    logging.debug(f"Logger initialized in mode {logging.getLevelName(log_level)}")


def _load_images(fileshelper: FilesHelper, dbhandler: DbHandler, imagemapper: ImageMapper, config: dict) -> dict:
    new_images, existing_images = ImageLoader(fileshelper, dbhandler, imagemapper, config).load_images()
    images = {
        'new': new_images,
        'existing': existing_images
    }

    return images
