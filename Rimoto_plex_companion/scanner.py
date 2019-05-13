import os
import sqlite3
import subprocess
from pathlib import Path, PureWindowsPath
from time import sleep
from datetime import datetime as dt

from tinydb import TinyDB
import hug
import logzero
from logzero import logger
from sqlalchemy import or_

from rimoto_plex_companion.db_init import Session, Media


base_rclone_media_path = "C:/Media"
remote_mount_folder_name = "gcache"
plex_db_path = "C:/.plex/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db"
logfile = "I:/Logs/Rimoto/scanner.log"
plex_scanner_path="E:/Utils/Plex/Plex Media Scanner.exe"
minutes_check_for_path_existence=1

logzero.logfile(logfile, maxBytes=4028)

path_keys = [
    ("Movies", "2"),
    ("Anime", "3"),
    ("Adult", "11"),
    ("Kids", "12"),
    ("Family", "13"),
]


session = Session()

def get_media_category(remote_file_path):
    for key,section in path_keys:
        if key in os.path.dirname(remote_file_path):
            return section

def remote_file_to_local_file(remote_file_path):
    file_path = base_rclone_media_path + remote_file_path.split(remote_mount_folder_name)[1]
    return PureWindowsPath(file_path)

def wait_path(windows_file_path):
    for i in range(minutes_check_for_path_existence*6):
        if Path(windows_file_path).exists():
            return True
        logger.warning(f"{windows_file_path} existense check {i}/{minutes_check_for_path_existence*6}")
        sleep(10)
    else:
        return False

def import_to_plex(windows_folder_path:Path , section):
    if not Path(windows_folder_path).is_dir():
        logger.error("Path is not a directory")
        return False
    logger.debug(f'Executing "{plex_scanner_path}" -c {section} -s -r --no-thumbs -d "{windows_folder_path}"')
    result = subprocess.Popen(f'"{plex_scanner_path}" -c {section} -s -r --no-thumbs -d "{windows_folder_path}"')
    try:
        while result.poll() is None:
            logger.debug("Waiting for Popen to end")
            sleep(60)
    except Exception as e:
        #TODO Figure what exceptions this can throw and narrow down the except clause
        logger.error(e)
        return False
    return True

def verify_import_in_db(windows_file_path: PureWindowsPath):
    plex_db = sqlite3.connect(plex_db_path)
    logger.debug(plex_db)
    cursor = plex_db.cursor()
    logger.debug(cursor)
    cursor.execute(f"SELECT * FROM media_parts WHERE file=?", (str(windows_file_path),))
    db_result = cursor.fetchone()
    logger.debug(db_result)
    try:
        logger.debug(f"We found it! {db_result}")
        response = dict(
            id=db_result[0],
            media_item_id=db_result[1],
            directory_id=db_result[2],
            hash=db_result[3],
            open_subtitle_hash=db_result[4],
            file=db_result[5],
            index=db_result[6],
            size=db_result[7],
            duration=db_result[8],
            created_at=db_result[9],
            deleted_at=db_result[10],
            extra_data=db_result[11],
        )        
    except Exception:
        #TODO Figure what exceptions this can throw and narrow down the except clause
        logger.error("File failed to import correctly")
        return False
    return response

def main():
    while True:
        for rec in session.query(Media).filter(or_(Media.downloaded_at > Media.scanned_at, Media.scanned_at.is_(None), Media.scanned_at.is_(None) )).all():
            logger.debug(rec)
            category = None
            local_path = None
            local_path_existence = None
            local_file_imported = None
            try:
                category = get_media_category(rec.path)
                local_path = remote_file_to_local_file(rec.path)
                local_path_existence = wait_path(local_path)
                if not local_path_existence:
                    if not rec.scan_attempts:
                        rec.scan_attempts = 1
                    else:
                        rec.scan_attempts += 1

                    logger.warning("Local path timed out. Not found.")
                    continue
                plex_import = import_to_plex(Path(local_path).parent, category)
                local_file_imported = verify_import_in_db(local_path)
                if local_file_imported:
                    rec.scanned_at = dt.utcnow()
            except OSError as e:
                logger.error(f"Failed to scan in file. Due to OSERROR\n\n{e}\n\nremote_path:{rec['remote_path']}\ncategory:{category}\nLocalPath:{local_path}")
        else:
            logger.info("No records found!")
            sleep(30)
        session.commit()
        sleep(30)
if __name__ == "__main__":
    main()