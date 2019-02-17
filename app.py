import logging
import os
import sqlite3
import subprocess
from pathlib import Path, PureWindowsPath
from time import sleep

from flask import Flask
from flask import jsonify
from flask import request

base_rclone_media_path = "C:/Media"
remote_mount_folder_name = "gcache"
plex_db_path = "C:/.plex/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db"

anime = ("Anime", "3")
adult = ("Adult", "11")
family = ("Family", "13")
kids = ("Kids", "12")
movies = ("Movies", "2")


app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)


@app.route("/scan", methods=["POST"])
def scan():
    logging.debug(f"Received {request.form['folder']}")
    if "Anime" in os.path.dirname(request.form["folder"]):
        section = "3"
        file_path = __translate_file_path(request.form["folder"])
        __wait_for_path(file_path)

    elif "Adult" in os.path.dirname(request.form["folder"]):
        section = "11"
        file_path = __translate_file_path(request.form["folder"])
        __wait_for_path(file_path)

    elif "Family" in os.path.dirname(request.form["folder"]):
        section = "13"
        file_path = __translate_file_path(request.form["folder"])
        __wait_for_path(file_path)

    elif "Kids" in os.path.dirname(request.form["folder"]):
        section = "12"
        file_path = __translate_file_path(request.form["folder"])
        __wait_for_path(file_path)

    elif "Movies" in os.path.dirname(request.form["folder"]):
        section = "2"
        file_path = __translate_file_path(request.form["folder"])
        __wait_for_path(file_path)
    else:
        return "False"

    logging.debug("The file exists! Now let's give it a little longer (2 mins)")
    sleep(1)

    while not __verify_import(request.form["folder"]):
        __scan(file_path, section)
    return jsonify(__verify_import(request.form["folder"]))


def __wait_for_path(path):
    logging.debug(f"Looking for {path}")
    p = path
    while not path.exists():
        logging.debug(f"Path does not exist: {path}")
        sleep(5)
    return path.exists()


def __translate_file_path(folder):
    base = base_rclone_media_path
    r_base = remote_mount_folder_name
    stripped_remote_path = folder.split(r_base)[1]
    logging.debug(f"stripped path: {str(stripped_remote_path)}")
    file_path = base + stripped_remote_path
    file_path = Path(file_path)
    logging.debug(f"Translated_file_path: {file_path}")
    return file_path


def __scan(folder, section):
    logging.debug(f"Scanning {folder} into {section}")
    result = subprocess.Popen(
        f'"E:/Utils/Plex/Plex Media Scanner.exe" -c {section} -s -r --no-thumbs -d "{folder.parent}"',
        stdout=subprocess.PIPE,
    )
    while result.poll() is None:
        sleep(5)


def __verify_import(file_name):
    file = __translate_file_path(file_name)
    file = PureWindowsPath(file)
    logging.debug(f"Verifying {file} was imported")
    db = sqlite3.connect(plex_db_path)
    cursor = db.cursor()
    logging.debug(f"Searching for {file} in db")
    cursor.execute(f"SELECT * FROM media_parts WHERE file=?", (str(file),))
    for row in cursor.fetchall():
        logging.debug(f"current row: {row}")
        try:
            logging.debug(f"We found it! {row[0]}")
            return dict(
                id=row[0], media_item_id=row[1],
                directory_id=row[2],
                hash=row[3],
                open_subtitle_hash=row[4],
                file=row[5],
                index=row[6],
                size=row[7],
                duration=row[8],
                created_at=row[9],
                deleted_at=row[10],
                extra_data=row[11])

        except Exception as e:
            logging.error(e)
            return False


def main():
    app.config["host"] = "0.0.0.0"
    app.config["debug"] = True
    app.config["port"] = 5000
    app.run()


if __name__ == "__main__":
    main()
