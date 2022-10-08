import unittest
from configparser import ConfigParser
from pathlib import Path
from src.detectors.sift import SiftDuplicateDetector


class TestSift(unittest.TestCase):
    def test_SiftDuplicateDetector(self):
        config = ConfigParser()
        config.read('./config.ini')

        images = load_images(config)

        expected = {
            'bmw.jpg',
            'bmw2_scaled_down.jpg',
            'bmw3.jpg',
        }

        options = {'config': config}
        result = SiftDuplicateDetector(
            images=images, **options).determine_duplicates()

        self.assertSetEqual(set(result), expected)


def load_images(config: ConfigParser) -> list:
    images = []

    for file in Path(config['unittests']['fixtures_dir']).iterdir():
        if not file.is_file():
            continue

        images.append(file.as_posix())

    return images
