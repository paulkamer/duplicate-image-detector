import logging
import os
import cv2
from .compare_image_renderers.sift import SiftCompareImageRenderer as ImageRenderer

BF_MATCHES_NORM_TYPE = cv2.NORM_L1


class SiftDuplicateDetector:
    def __init__(self, new_images: dict, existing_images: dict, **options):
        self.__new_images = new_images
        self.__existing_images = existing_images

        self.__computed_images = {}
        self.__duplicates = {}

        self.__render_comparisons = options.get('render_comparison_images')
        self.__config = options.get('config')['sift']

        self.__bfMatcher = cv2.BFMatcher(BF_MATCHES_NORM_TYPE, crossCheck=True)
        self.__sift = cv2.SIFT_create(
            edgeThreshold=int(self.__config['edge_threshold']))

    def detect(self):
        self.__compute_sift_keypoints_and_descriptors()

        self.__find_duplicates()

        if (self.__render_comparisons):
            ImageRenderer(self.__duplicates, self.__computed_images).render()

        return self.__duplicates

    def __compute_sift_keypoints_and_descriptors(self):
        for path in self.__new_images + self.__existing_images:
            image = cv2.imread(path)
            grey_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            keypoints, descriptors = self.__sift.detectAndCompute(
                grey_image, None)

            self.__computed_images[os.path.basename(path)] = {
                'kp': keypoints,
                'ds': descriptors,
                'img': grey_image
            }

    def __find_duplicates(self):
        for image in self.__new_images:
            filename = os.path.basename(image)
            logging.debug(f"Checking duplicates for {filename}...")

            self.__find_duplicate_for_image(filename)

    def __find_duplicate_for_image(self, source_image: str):
        similar_images = {source_image: {}}

        for image in self.__computed_images.keys():
            if image == source_image:
                continue

            descriptor_matches = self.__bfMatcher.match(
                self.__computed_images[source_image]['ds'],
                self.__computed_images[image]['ds']
            )

            # Discard if image is not similar enough
            if (len(descriptor_matches) < int(self.__config['duplicate_descriptor_matches_threshold'])):
                continue

            similar_images[source_image][image] = {
                'matches': descriptor_matches
            }

        if (similar_images[source_image]):
            self.__duplicates[source_image] = self.__sort_by_similarity(
                similar_images[source_image])

    def __sort_by_similarity(self, images):
        return {k: v for k, v in sorted(
            images.items(), key=lambda x: len(x[1]['matches']), reverse=True)}
