import os
import json
import logging

from .db import DbHandler
from .image import Image
from .fileshelper import FilesHelper
from .image_mapper import ImageMapper


class NewUniqueImagesHandler:
    def __init__(self, fileshelper: FilesHelper, imagemapper: ImageMapper, dbhandler: DbHandler):
        self.fileshelper = fileshelper
        self.imagemapper = imagemapper
        self.dbhandler = dbhandler

    def handle(self, images: list[Image], computed_images: dict):
        logging.debug(f"Storing new unique images")

        for image in images:
            dest = self.fileshelper.store_new_image(image.filename)

            img = self.imagemapper.serialize(
                dest,
                computed_images[image.filename]['kp'],
                computed_images[image.filename]['ds'].tolist()  # todo remove .tolist() here
            )

            self.dbhandler.store_image(img)
