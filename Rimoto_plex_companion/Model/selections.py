"""Brains behind the API."""
from pathlib import Path, PureWindowsPath
import os
from datetime import datetime as dt
import subprocess
from time import sleep

import hug
import logzero

from Rimoto_plex_companion.Model.rimoto_db import Rimoto
from Rimoto_plex_companion.Model.rimoto_db import Session as rimoto_session
from Rimoto_plex_companion.Model.plex_db import Plex
from Rimoto_plex_companion.Model.plex_db import Session as plex_session

logzero.logfile('E:/logs/rimoto_api.log')
LOGGER = logzero.logger


def count_all_records():
    session = rimoto_session()
    data = session.query(Rimoto).count()
    rimoto_session.remove()
    return data


def list_unscanned():
    session = rimoto_session()
    rows = session.query(Rimoto).filter((Rimoto.downloaded_at > Rimoto.scanned_at) | (Rimoto.scanned_at.is_(None))).all()
    rimoto_session.remove()

    return [{
        'id': row.id,
        'path': row.path,
        'remote_path': row.remote_path,
        'exists_locally': row.exists_locally,
        'downloaded_at': row.downloaded_at,
        'scanned_at': row.scanned_at,
        'version_number': row.version_number,
        'scan_attempts': row.scan_attempts,
        'library_name': row.library_name,
        'library_id': row.library_id
    } for row in rows]


def list_recently_scanned(limit: hug.types.number = 20):
    session = rimoto_session()
    rows = session.query(Rimoto).order_by(Rimoto.scanned_at.desc()).limit(limit)
    rimoto_session.remove()
    return [{
        'id': row.id,
        'path': row.path,
        'downloaded_at': row.downloaded_at,
        'scanned_at': row.scanned_at,
        'version_number': row.version_number,
        'scan_attempts': row.scan_attempts,
    } for row in rows]


def delete_from_queue(path):
    session = rimoto_session()
    session.query(Rimoto).filter_by(path=path).delete()
    session.commit()
    rimoto_session.remove()


def convert_to_local_path(path):
    base_media_path = "C:/Media"
    remote_mount_folder_name = "gcache"
    universal_path = path.split(remote_mount_folder_name)[1]
    file_path = base_media_path + universal_path
    local_file_path = PureWindowsPath(file_path)
    return local_file_path


def media_group(path):
    plex_libs = dict(
        Movies='2',
        Anime='3',
        Adult='11',
        Kids='12',
        Family='13'
    )
    directory = os.path.dirname(path)
    for lib_name, lib_id in plex_libs.items():
        if lib_name in directory:
            result = lib_name, lib_id
    return result


def add_to_queue(path):
    session = rimoto_session()
    local_path = convert_to_local_path(path)
    library = media_group(local_path)
    row = Rimoto(path=str(local_path), remote_path=path, library_name=library[0], library_id=library[1])
    session.add(row)
    session.commit()
    row = session.query(Rimoto).filter_by(remote_path=path).first()
    rimoto_session.remove()
    data = [{
        'id': row.id,
        'path': row.path,
        'remote_path': row.remote_path,
        'exists_locally': row.exists_locally,
        'downloaded_at': row.downloaded_at,
        'scanned_at': row.scanned_at,
        'version_number': row.version_number,
        'scan_attempts': row.scan_attempts,
        'library_name': row.library_name,
        'library_id': row.library_id
    }]
    print(data)
    return data


def check_import(path):
    session = plex_session()
    db_result = session.query(Plex).filter(
        Plex.file == path).first()
    plex_session.remove()
    if db_result:
        return dict(id=db_result.id, file=db_result.file)
    return dict()


def local_path_exists(path):
    return Path(path).exists()


def plex_scanner(path, section):
    scanner_path = "E:/Utils/Plex/Plex Media Scanner.exe"
    command = f'"{scanner_path}" -c {section} -s -r --no-thumbs -d "{os.path.dirname(path)}"'
    result = subprocess.Popen(command)
    result.wait()


def manual_import(path, section_id, _id):
    r_session = rimoto_session()
    if not local_path_exists(path):
        rimoto_session.remove()
        plex_session.remove()
        return "Path not available yet"
    plex_scanner(path, section_id)
    if not check_import(path):
        rimoto_session.remove()
        plex_session.remove()
        return "Failed to import"
    record = r_session.query(Rimoto).filter(Rimoto.id == _id).first()
    record.scanned_at = dt.now()
    r_session.commit()
    rimoto_session.remove()
    plex_session.remove()
    return None


def scan_all():
    unscanned = list_unscanned()
    for media in unscanned:
        manual_import(media['path'],
                      media['library_id'],
                      media['id'])
        sleep(10)
