from .fileshelper import FilesHelper


class ImageLoader:
    def __init__(self, fileshelper: FilesHelper, config: dict):
        self.fileshelper = fileshelper
        self.config = config

    def load_images(self):
        # TODO map to Image objects
        new_images = self.fileshelper.load_images(self.config['paths']['new_images_dir'])
        existing_images = self.fileshelper.load_images(self.config['paths']['images_dir'])

        return new_images, existing_images
