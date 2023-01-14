import logging
from .fileshelper import FilesHelper


class DuplicatesHandler:
    def __init__(self, fileshelper: FilesHelper, options: dict):
        self.fileshelper = fileshelper
        self.options = options

    def handle(self, duplicates: dict):
        logging.info(f"Duplicates found: {len(duplicates)}")

        if (duplicates):
            self._log_duplicates(duplicates)

            if (self.options.get('remove_duplicates')):
                self.fileshelper.delete_duplicates(duplicates.keys())
            else:
                self.fileshelper.move_duplicates(duplicates.keys())

    def _log_duplicates(self, duplicates: dict):
        for key in duplicates:
            logging.info(key)

            for duplicate in duplicates[key]:
                logging.info(f"\t- {duplicate} - {len(duplicates[key][duplicate]['matches'])} matched descriptors")
