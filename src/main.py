import argparse
import imghdr
from pathlib import Path

from detectors.sift import SiftDuplicateDetector

IMAGES_DIR = './images'
SUPPORTED_IMAGE_TYPES = ['jpg', 'jpeg', 'png']

def main(debug: bool = False, render_comparison_images: bool = False):
    print('Main')
    images = load_images(IMAGES_DIR)
    
    duplicate_detector = SiftDuplicateDetector(images)
    duplicates = duplicate_detector.determine_duplicates()
    
    print(len(images))
    print(f"Duplicates: {duplicates}")
    print(f"Unique duplicates: {list(set(duplicates))}")
    
def load_images(dir: str):
    images = []

    for file in Path(dir).iterdir():
        if not file.is_file(): continue

        path = file.as_posix()

        # Check if it's a supported image
        filetype = imghdr.what(path)
        if (filetype not in SUPPORTED_IMAGE_TYPES):
            print('Unsupported file type: ' + filetype)
            continue

        images.append(path)

    return images
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d',
        "--debug",
        help="Log debug output",
        action='store_const',
        const=True
    )
    parser.add_argument(
        "--render",
        help="render comparison image of most similar duplicate image",
        action='store_const',
        const=True
    )
    
    args = parser.parse_args()
    
    main(args.debug, args.render)    