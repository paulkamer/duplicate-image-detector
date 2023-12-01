import cv2
import copyreg
import logging
from multiprocessing import Process, Manager
from .compare_image_renderers.sift import SiftCompareImageRenderer as ImageRenderer
from ..image import Image

BF_MATCHES_NORM_TYPE = cv2.NORM_L1


class SiftDuplicateDetector:
    def __init__(self, images: dict[str, list[Image]], options: dict):
        self._manager = Manager()

        self._new_images = images['new']
        self._existing_images = images['existing']

        self._duplicates = self._manager.dict()
        self._computed_images = self._manager.dict()

        self._render_comparisons = options.get('render_comparison_images')
        self._config = options.get('config')['sift']

        self._descriptor_matcher = cv2.BFMatcher(BF_MATCHES_NORM_TYPE, crossCheck=True)
        self._sift = cv2.SIFT_create(edgeThreshold=int(self._config['edge_threshold']))

    def detect(self):
        logging.debug("Running SIFT duplicate detector...")
        self._compute_sift_keypoints_and_descriptors()

        similar_images = self._manager.dict()
        self._find_duplicates_in_new_images(similar_images)
        self._find_similar_images_in_existing_images(similar_images)

        if (self._render_comparisons):
            ImageRenderer(self._duplicates, self._computed_images).render()

    def get_computed_images(self):
        return self._computed_images

    def get_duplicates(self):
        return self._duplicates

    def _compute_sift_keypoints_and_descriptors(self):
        logging.debug("Computing keypoints & descriptors using SIFT...")

        processes = []
        for image in self._new_images + self._existing_images:
            processes.append(Process(target=SiftDuplicateDetector._compute_image,
                             args=(self._sift, self._computed_images, image)))

        [p.start() for p in processes]
        [p.join() for p in processes]

    @staticmethod
    def _compute_image(sift, computed_images: dict, image: Image):
        path = image.filename
        logging.debug(f"Computing {path}")

        img = cv2.imread(path)
        grey_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        kp = None
        ds = None
        if (image.metadata):
            logging.debug('Relying on cached metadata')

            kp = image.metadata['keypoints']
            ds = image.metadata['descriptors']

        else:
            kp, ds = sift.detectAndCompute(grey_image, None)

        computed_images[path] = {'kp': kp, 'ds': ds, 'img': grey_image}

    def _find_duplicates_in_new_images(self, similar_images: dict):
        logging.debug("Checking for duplicates in new images...")

        self._find_duplicates(self._new_images, similar_images)

    def _find_similar_images_in_existing_images(self, similar_images: dict):
        logging.debug("Chking for similar images in existing images collection...")

        self._find_duplicates(self._existing_images, similar_images)

    def _find_duplicates(self, images: list[Image], similar_images: dict):
        logging.debug("Checking for duplicates in new images...")

        # Check if new_images list contains duplicates first
        for image in self._new_images:
            filename = image.filename

            self._find_duplicate_for_image(filename, images, similar_images)

            if (similar_images[filename]):
                self._duplicates[filename] = self._sort_duplicates(similar_images[filename])

    def _find_duplicate_for_image(self, source_image: str, images: list[Image], similar_images: dict):
        logging.debug(f"Checking duplicates for {source_image}...")

        similar_images.update({source_image: {}})

        min_matches = int(self._config['duplicate_descriptor_matches_threshold'])

        processes = []
        for image in images:
            filename = image.filename

            if source_image == filename:
                continue

            processes.append(
                Process(target=SiftDuplicateDetector._find_matches, args=(self._descriptor_matcher, min_matches,
                        self._computed_images, similar_images, source_image, filename))
            )

        [p.start() for p in processes]
        [p.join() for p in processes]

    @staticmethod
    def _find_matches(matcher, min_matches, computed_images, similar_images, source_image, filename):
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

    def _sort_duplicates(self, images):
        """
        Sort duplicate images on number of descriptor matches
        """
        return {k: v for k, v in sorted(images.items(), key=lambda x: x[1]['matches'], reverse=True)}


def _pickle_keypoints(point):
    """
    Ensure cv2.KeyPoint objects can be pickled. https://stackoverflow.com/a/48832618
    """
    return cv2.KeyPoint, (*point.pt, point.size, point.angle, point.response, point.octave, point.class_id)


def _pickle_dmatch(dmatch):
    """
    Ensure cv2.DMatch objects can be pickled
    """
    return cv2.DMatch, (dmatch.queryIdx,  dmatch.trainIdx, dmatch.imgIdx, dmatch.distance)


copyreg.pickle(cv2.KeyPoint().__class__, _pickle_keypoints)
copyreg.pickle(cv2.DMatch().__class__, _pickle_dmatch)
