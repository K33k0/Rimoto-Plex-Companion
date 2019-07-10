import os
from pathlib import PureWindowsPath
import sys

from Rimoto_plex_companion.add_to_db import db


def _convert_to_local_path(path):
    base_media_path = "C:/Media"
    remote_mount_folder_name = "gcache"
    universal_path = path.split(remote_mount_folder_name)[1]
    file_path = base_media_path + universal_path
    local_file_path = PureWindowsPath(file_path)
    return local_file_path


def _get_library_id(path):
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


def main(path=None):
    if not path:
        try:
            path = sys.argv[1]
        except IndexError:
            print("A path was expected")
            return

    session = db.Session()
    windows_path = _convert_to_local_path(path)
    library_id = _get_library_id(windows_path)
    row = db.Media(vps_path=str(path),
                   plex_library_id=library_id[1],
                   server_path=str(windows_path))
    session.add(row)
    session.commit()
    db.Session.remove()
