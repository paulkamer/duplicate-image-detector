import logging
import os
import cv2
from .compare_image_renderers.sift import SiftCompareImageRenderer as ImageRenderer

BF_MATCHES_NORM_TYPE = cv2.NORM_L1


class SiftDuplicateDetector:
    def __init__(self, images: dict, **options):
        self._images = images
        self._computed_images = {}
        self._duplicates = {}

        self._render_comparison_images = options.get(
            'render_comparison_images')
        self._config = options.get('config')['sift']

    def determine_duplicates(self):
        bfMatcher = cv2.BFMatcher(BF_MATCHES_NORM_TYPE, crossCheck=True)

        self.compute_sift_keypoints_and_descriptors()

        for image in self._computed_images.keys():
            filename = os.path.basename(image)
            logging.debug(f"Checking duplicates for {filename}...")

            self.find_duplicates(filename, bfMatcher)

        if (self._render_comparison_images):
            ImageRenderer(self._duplicates, self._computed_images).render()

        return self._duplicates

    def compute_sift_keypoints_and_descriptors(self):
        sift = cv2.SIFT_create(edgeThreshold=int(
            self._config['edge_threshold']))

        for path in self._images:
            image = cv2.imread(path)
            grey_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            keypoints, descriptors = sift.detectAndCompute(
                grey_image, None)

            self._computed_images[os.path.basename(path)] = {
                'kp': keypoints,
                'ds': descriptors,
                'img': grey_image
            }

    def find_duplicates(self, source_image: str, bfMatcher):
        similar_images = {source_image: {}}

        for image in self._computed_images.keys():
            if image == source_image:
                continue

            descriptor_matches = bfMatcher.match(
                self._computed_images[source_image]['ds'], self._computed_images[image]['ds'])

            # Discard if image is not similar enough
            if (len(descriptor_matches) < int(self._config['duplicate_descriptor_matches_threshold'])):
                continue

            similar_images[source_image][image] = {
                'matches': descriptor_matches
            }

        if (similar_images[source_image]):
            self._duplicates[source_image] = self.sort_by_similarity(
                similar_images[source_image])

    def sort_by_similarity(self, images):
        return {k: v for k, v in sorted(
            images.items(), key=lambda x: len(x[1]['matches']), reverse=True)}
