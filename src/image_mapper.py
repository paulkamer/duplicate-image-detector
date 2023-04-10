import cv2
import json
import numpy as np

from .image import Image


class ImageMapper:
    def hydrate(self, filename: str) -> Image:
        return Image(filename)

    def hydrate_from_db(self, image: tuple) -> Image:
        metadata = json.loads(image[1])

        if (not metadata):
            return Image(image[0])

        hydrated_metadata = {
            'keypoints': self._hydrate_keypoints(metadata['keypoints']),
            'descriptors': self._hydrate_descriptors(metadata['descriptors'])
        }

        return Image(image[0], hydrated_metadata)

    def _hydrate_keypoints(self, serialized_keypoints: str) -> list[cv2.KeyPoint]:
        return [self._map_keypoint_to_object(k) for k in json.loads(serialized_keypoints)]

    def _map_keypoint_to_object(self, kp: dict) -> cv2.KeyPoint:
        return cv2.KeyPoint(kp['pt'][0], kp['pt'][1], kp['size'], kp['angle'], kp['response'], kp['octave'], kp['class_id'])

    def _hydrate_descriptors(self, serialized_descriptors: str):
        return [self._map_descriptor_to_object(ds) for ds in json.loads(serialized_descriptors)]

    def _map_descriptor_to_object(self, ds: dict) -> np.ndarray:
        return np.asarray(ds)

    def serialize(self, filename: str, keypoints: list[cv2.KeyPoint], descriptors: list) -> Image:
        metadata = self._serialize_metadata(keypoints, descriptors)

        return Image(filename, metadata)

    def _serialize_metadata(self, keypoints: list[cv2.KeyPoint], descriptors: list) -> dict:
        keypoints = [self._serialize_keypoint(kp) for kp in keypoints]

        return {
            'keypoints': json.dumps(keypoints),
            'descriptors': json.dumps(descriptors)
        }

    def _serialize_keypoint(self, kp: cv2.KeyPoint) -> dict:
        return {
            'pt': kp.pt,
            'size': kp.size,
            'angle': kp.angle,
            'response': kp.response,
            'octave': kp.octave,
            'class_id': kp.class_id,
        }
