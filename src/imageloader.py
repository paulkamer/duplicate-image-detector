from .db.dbhandler import DbHandler
from .fileshelper import FilesHelper
from .image import Image
from .image_mapper import ImageMapper


class ImageLoader:
    def __init__(self, fileshelper: FilesHelper, dbhandler: DbHandler, imagemapper: ImageMapper, config: dict):
        self.fileshelper = fileshelper
        self.dbhandler = dbhandler
        self.imagemapper = imagemapper
        self.config = config

    def load_images(self) -> list:
        return self._load_new_images(), self._load_existing_images()

    def _load_new_images(self):
        return self._load_images(self.config['paths']['new_images_dir'])

    def _load_images(self, path: str):
        images = self.fileshelper.load_images(path)
        return self._map_images(images)

    def _map_images(self, images: list[str]) -> list[Image]:
        return [self.imagemapper.hydrate(filename) for filename in images]

    def _load_existing_images(self):
        cached_images = self.dbhandler.fetch_images()

        # If no images were cached in the DB, fetch them from the file system
        if (not cached_images):
            return self._load_images(self.config['paths']['images_dir'])

        return self._map_cached_images(cached_images)

    def _map_cached_images(self, images: list[tuple]) -> list[Image]:
        return [self.imagemapper.hydrate_from_db(image) for image in images]
