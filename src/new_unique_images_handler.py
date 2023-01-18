import os
import json
import logging

from .db import DbHandler
from .image import Image
from .fileshelper import FilesHelper


class NewUniqueImagesHandler:
    def __init__(self, fileshelper: FilesHelper, dbhandler: DbHandler, config: dict):
        self.fileshelper = fileshelper
        self.dbhandler = dbhandler
        self.config = config

    def handle(self, images: list[str], computed_images: dict):
        logging.debug(f"Storing new unique images")

        for filename in images:
            self.fileshelper.store_new_image(filename)

            metadata = self._format_metadata(filename, computed_images)

            image = Image(os.path.basename(filename), metadata)

            self.dbhandler.store_image(image)

    def _format_metadata(self, image: str, computed_images: dict) -> Image:
        keypoints = [{
            'pt': k.pt,
            'size': k.size,
            'angle': k.angle,
            'response': k.response,
            'octave': k.octave,
            'class_id': k.class_id,
        } for k in computed_images[image]['kp']]

        return {
            'keypoints': json.dumps(keypoints),
            'descriptors': json.dumps(computed_images[image]['ds'].tolist())
        }
