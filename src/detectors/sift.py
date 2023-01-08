import cv2
import copyreg
import logging
from multiprocessing import Process, Manager
from .compare_image_renderers.sift import SiftCompareImageRenderer as ImageRenderer

BF_MATCHES_NORM_TYPE = cv2.NORM_L1


class SiftDuplicateDetector:
    def __init__(self, new_images: dict, existing_images: dict, config: dict, render_comparisons: bool):
        self.__manager = Manager()

        self.__new_images = new_images
        self.__existing_images = existing_images

        self.__duplicates = self.__manager.dict()
        self.__computed_images = self.__manager.dict()

        self.__render_comparisons = render_comparisons
        self.__config = config

        self.__descriptor_matcher = cv2.BFMatcher(BF_MATCHES_NORM_TYPE, crossCheck=True)
        self.__sift = cv2.SIFT_create(edgeThreshold=int(config['edge_threshold']))

    def detect(self):
        logging.debug("Running SIFT duplicate detector...")
        self.__compute_sift_keypoints_and_descriptors()

        self.__find_duplicates()

        if (self.__render_comparisons):
            ImageRenderer(self.__duplicates, computed_images).render()

        return self.__duplicates  # TODO return simple dict/list

    def __compute_sift_keypoints_and_descriptors(self):
        logging.debug("Computing keypoints & descriptors using SIFT...")

        processes = []
        for path in self.__new_images + self.__existing_images:
            processes.append(Process(target=SiftDuplicateDetector.__compute_image,
                             args=(self.__sift, self.__computed_images, path)))

        [p.start() for p in processes]
        [p.join() for p in processes]

    @staticmethod
    def __compute_image(sift, computed_images, path):
        logging.debug(f"Computing {path}")

        image = cv2.imread(path)
        grey_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        kp, ds = sift.detectAndCompute(grey_image, None)

        computed_images[path] = {'kp': kp, 'ds': ds, 'img': grey_image}

    def __find_duplicates(self):
        logging.debug("Checking for duplicates...")
        similar_images = self.__manager.dict()

        for image in self.__new_images:
            filename = image

            self.__find_duplicate_for_image(filename, similar_images)

            if (similar_images[filename]):
                self.__duplicates[filename] = self.__sort_duplicates(similar_images[filename])

    def __find_duplicate_for_image(self, source_image: str, similar_images: dict):
        logging.debug(f"Checking duplicates for {source_image}...")

        similar_images.update({source_image: {}})

        min_matches = int(self.__config['duplicate_descriptor_matches_threshold'])

        processes = []
        for image in self.__existing_images:
            filename = image

            processes.append(
                Process(target=SiftDuplicateDetector.__find_matches, args=(self.__descriptor_matcher, min_matches,
                        self.__computed_images, similar_images, source_image, filename))
            )

        [p.start() for p in processes]
        [p.join() for p in processes]

    @staticmethod
    def __find_matches(matcher, min_matches, computed_images, similar_images, source_image, filename):
        descriptor_matches = matcher.match(computed_images[source_image]['ds'], computed_images[filename]['ds'])

        # Discard if image is not similar enough
        if (len(descriptor_matches) < min_matches):
            return

        similar_images.update(
            {
                source_image: {
                    filename: {
                        'matches': descriptor_matches
                    }
                }
            }
        )

    def __sort_duplicates(self, images):
        """
        Sort duplicate images on number of descriptor matches
        """
        return {k: v for k, v in sorted(images.items(), key=lambda x: x[1]['matches'], reverse=True)}


def _pickle_keypoints(point):
    """
    Ensure v2.KeyPoint objects can be pickled. https://stackoverflow.com/a/48832618
    """
    return cv2.KeyPoint, (*point.pt, point.size, point.angle, point.response, point.octave, point.class_id)


def _pickle_dmatch(dmatch):
    """
    Ensure cv2.DMatch objects can be pickled
    """
    return cv2.DMatch, (dmatch.imgIdx, dmatch.queryIdx, dmatch.trainIdx)


copyreg.pickle(cv2.KeyPoint().__class__, _pickle_keypoints)
copyreg.pickle(cv2.DMatch().__class__, _pickle_dmatch)
