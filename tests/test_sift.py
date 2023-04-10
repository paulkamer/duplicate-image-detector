import unittest
from configparser import ConfigParser
from pathlib import Path
from src.detectors.sift import SiftDuplicateDetector
from src.image import Image


class TestSift(unittest.TestCase):
    def test_SiftDuplicateDetector(self):
        config = ConfigParser()
        config.read('./config.ini')

        images = {
            'new': load_images(config['unittests']['fixtures_dir'] + "/new"),
            'existing': load_images(config['unittests']['fixtures_dir'] + "/store")
        }

        expected = {
            'tests/fixtures/new/bmw3.jpg',
            'tests/fixtures/new/bmw2_scaled_down.jpg',
        }

        options = {'config': config}
        sut = SiftDuplicateDetector(images=images, options=options)
        sut.detect()

        result = sut.get_duplicates()

        self.assertSetEqual(set(result), expected)


def load_images(path: str) -> list:
    images = []

    for file in Path(path).iterdir():
        if not file.is_file():
            continue

        images.append(Image(file.as_posix()))

    return images
