import sqlite3
import json
from ..metaclasses.singleton import Singleton
from ..image import Image


class DbHandler:
    def __init__(self, config: dict, metaclass=Singleton):
        self._config = config
        self._con = sqlite3.connect(config['db']['database_path'])

        self._init_db()

    def fetch_images(self):
        cur = self._con.cursor()

        res = cur.execute("SELECT * FROM images")
        results = res.fetchall()
        cur.close()

        return results

    def store_image(self, image: Image):
        cur = self._con.cursor()

        cur.execute("INSERT INTO images (filename, metadata) VALUES (?,?)",
                    (image.filename, json.dumps(image.metadata)))

        self._con.commit()
        cur.close()

    def _init_db(self):
        cur = self._con.cursor()

        cur.execute("""
                    CREATE TABLE IF NOT EXISTS images (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        filename TEXT NOT NULL UNIQUE, 
                        metadata TEXT
                    )
                    """)

        cur.close()

    def __del__(self):
        self._con.close()
