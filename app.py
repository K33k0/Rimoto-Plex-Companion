import os
import sqlite3
import subprocess
from pathlib import Path, PureWindowsPath
from time import sleep

import hug
from logzero import logger

base_rclone_media_path = "C:/Media"
remote_mount_folder_name = "gcache"
plex_db_path = "C:/.plex/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db"

path_keys = [
    ("Movies", "2"),
    ("Anime", "3"),
    ("Adult", "11"),
    ("Kids", "12"),
    ("Family", "13"),
]


@hug.cli()
@hug.get("/scan")
def scan(remote_file_path, request):
    logger.info(f"Request from {request.headers['X-REAL-IP']} to {path}")
    file_path, section = __categorize(remote_file_path)
    if not __wait_grace_period(file_path):
        return False
    while not __verify_import(remote_file_path):
        __scan(file_path, section)
    return __verify_import(remote_file_path)


def __wait_grace_period(file_path):
    if file_path:
        logger.debug("The file exists! Now let's give it a little longer (30 Seconds)")
        sleep(30)
        return True
    return False


def __categorize(file_path):
    for key, section in path_keys:
        if key in os.path.dirname(file_path):
            file_path = __translate_file_path(file_path)
            __wait_for_path(file_path)
            return file_path, section


def __wait_for_path(path):
    logger.debug(f"Looking for {path}")
    while not path.exists():
        logger.debug(f"Path does not exist: {path}")
        sleep(5)
    return path.exists()


def __translate_file_path(folder):
    base = base_rclone_media_path
    r_base = remote_mount_folder_name
    stripped_remote_path = folder.split(r_base)[1]
    logger.debug(f"stripped path: {str(stripped_remote_path)}")
    file_path = base + stripped_remote_path
    file_path = Path(file_path)
    logger.debug(f"Translated_file_path: {file_path}")
    return file_path


def __read_db(file_path):
    db = sqlite3.connect(plex_db_path)
    cursor = db.cursor()
    logger.debug(f"Searching for {file_path} in db")
    cursor.execute(f"SELECT * FROM media_parts WHERE file=?", (str(file_path),))
    return cursor.fetchone()


def __scan(folder, section):
    logger.debug(f"Scanning {folder} into {section}")
    result = subprocess.Popen(
        f'"E:/Utils/Plex/Plex Media Scanner.exe" -c {section} -s -r --no-thumbs -d "{folder.parent}"',
        stdout=subprocess.PIPE,
    )
    try:
        while result.poll() is None:
            sleep(5)
    except Exception:
        return False
    return True


def __verify_import(file_name):
    file = __translate_file_path(file_name)
    file = PureWindowsPath(file)
    logger.debug(f"Verifying {file} was imported")
    row = __read_db(file)
    try:
        logger.debug(f"We found it! {row[0]}")
        return dict(
            id=row[0],
            media_item_id=row[1],
            directory_id=row[2],
            hash=row[3],
            open_subtitle_hash=row[4],
            file=row[5],
            index=row[6],
            size=row[7],
            duration=row[8],
            created_at=row[9],
            deleted_at=row[10],
            extra_data=row[11],
        )

    except Exception as e:
        logger.error(e)
        return False
