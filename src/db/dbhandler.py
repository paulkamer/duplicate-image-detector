import sqlite3
import json
DATABASE = "images.db"


def fetch_images():
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()

    res = cur.execute("SELECT * FROM images")
    results = res.fetchall()


def store_image(filename: str, sift_keypoints: list, sift_descriptors: list):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()

    keypoints = [{
        'pt': k.pt,
        'size': k.size,
        'angle': k.angle,
        'response': k.response,
        'octave': k.octave,
        'class_id': k.class_id,
    } for k in sift_keypoints]

    cur.execute("""
                INSERT INTO images (filename, sift_keypoints, sift_descriptors)
                VALUES (?,?, ?)
                """, (filename, json.dumps(keypoints), json.dumps(sift_descriptors.tolist())))

    con.commit()

    con.close()


def init_db():
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()

    cur.execute("""
                CREATE TABLE IF NOT EXISTS images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    filename TEXT NOT NULL UNIQUE, 
                    sift_keypoints TEXT, 
                    sift_descriptors TEXT
                )
                """)

    con.close()
