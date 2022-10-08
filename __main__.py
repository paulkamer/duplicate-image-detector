import argparse
import logging
from configparser import ConfigParser

from src import app

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
    parser.add_argument(
        "--restore",
        help="Move images in duplicates dir back to images dir",
        action='store_const',
        const=True
    )

    args = parser.parse_args()

    options = {
        'debug': args.debug,
        'render_comparison_images': args.render,
        'restore': args.restore
    }

    level = logging.DEBUG if options['debug'] == True else logging.WARN
    logging.basicConfig(encoding='utf-8', level=level)

    config = ConfigParser()
    config.read('config.ini')

    options['config'] = config

    app(**options)
