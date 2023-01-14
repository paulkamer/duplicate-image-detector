class Image:
    def __init__(self, filename: str, metadata: dict):
        self.filename = filename
        self.metadata = metadata

    def __str__(self):
        return self.filename
