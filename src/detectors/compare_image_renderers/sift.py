import cv2
import logging
import matplotlib.pyplot as plt


class SiftCompareImageRenderer:
    def __init__(self, duplicates: dict, computed_images: dict):
        self._duplicates = duplicates
        self._computed_images = computed_images

    def render(self):
        logging.debug('Rendering SIFT compare images')
        for image in self._duplicates.keys():
            first_match_filename = list(self._duplicates[image].keys())[0]

            img1 = self._computed_images[image]['img']
            kp1 = self._computed_images[image]['kp']
            img2 = self._computed_images[first_match_filename]['img']
            kp2 = self._computed_images[first_match_filename]['kp']
            matches = self._duplicates[image][first_match_filename]['matches'][:50]

            dup = cv2.drawMatches(img1, kp1, img2, kp2, matches,
                                  None, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

            plt.figure(image)
            plt.imshow(dup)
            plt.show()
