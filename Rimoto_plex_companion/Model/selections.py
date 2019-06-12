from pathlib import Path, PureWindowsPath
import os
from datetime import datetime as dt
import subprocess
from time import sleep
from datetime import datetime as dt
import logzero
logzero.logfile('E:/logs/rimoto_api.log')
logger = logzero.logger

def count_all_records(session,table):
    return session.query(table).count()

def list_unscanned(session,table,limit=20):
    rows = session.query(table).filter((
        table.downloaded_at > table.scanned_at
    ) | (
        table.scanned_at.is_(None)
    )).all()

    return [{
        'id':row.id,
        'path':row.path,
        'remote_path': row.remote_path,
        'exists_locally': row.exists_locally,
        'downloaded_at':row.downloaded_at,
        'scanned_at':row.scanned_at,
        'version_number':row.version_number,
        'scan_attempts':row.scan_attempts,
        'library_name': row.library_name,
        'library_id': row.library_id
    } for row in rows]        

def list_recently_scanned(session, table, limit=20):
    rows = session.query(table).order_by(table.scanned_at.desc()).limit(limit)
    return [{
        'id':row.id,
        'path':row.path,
        'downloaded_at':row.downloaded_at,
        'scanned_at':row.scanned_at,
        'version_number':row.version_number,
        'scan_attempts':row.scan_attempts,
    } for row in rows]

def delete_from_queue(session, table, path):
    session.query(table).filter_by(path=path).delete()
    session.commit()

def convert_to_local_path(path):
    base_media_path = "C:/Media"
    remote_mount_folder_name = "gcache"
    universal_path = path.split(remote_mount_folder_name)[1]
    file_path = base_media_path + universal_path
    local_file_path = PureWindowsPath(file_path)
    return local_file_path

def media_group(path):
    media_path_keys = [
    ("Movies", "2"),
    ("Anime", "3"),
    ("Adult", "11"),
    ("Kids", "12"),
    ("Family", "13")]
    for folder_section_name, plex_library_id in media_path_keys:
        directory = os.path.dirname(path)
        if folder_section_name in directory:
            return folder_section_name, plex_library_id

def add_to_queue(session, table, path):
    local_path = convert_to_local_path(path)
    library = media_group(local_path)
    row = table(path=str(local_path),remote_path=path, library_name=library[0], library_id=library[1])
    session.add(row)
    session.commit()

def check_import(session, table, path):
    """Check for path in plex db. Verifies the import was successful"""
    db_result = session.query(table).filter(
        table.file==path).first()
    if db_result:
        return dict(id=db_result.id, file=db_result.file)
    return False

def local_path_exists(path):
    return Path(path).exists()

def plex_scanner(path, section):
    scanner_path = "E:/Utils/Plex/Plex Media Scanner.exe"
    command = f'"{scanner_path}" -c {section} -s -r --no-thumbs -d "{os.path.dirname(path)}"'
    result = subprocess.Popen(command)
    result.wait()
    
def manual_import(path, section_id, plex_session, plex_table, rim_table, rim_session, id):
    logger.info(f'Starting scan for {path}')
    if not local_path_exists(path):
        logger.warning(f'{path} not yet available')
        return "Path not available yet"
    plex_scanner(path, section_id)
    if not check_import(plex_session, plex_table, path):
        return "Failed to import"
    record = rim_session.query(rim_table).filter(rim_table.id==id).first()
    record.scanned_at = dt.now()
    rim_session.commit()
    
def scan_all(plex_session, plex_table, rimoto_session, rimoto_table):
    unscanned = list_unscanned(rimoto_session, rimoto_table, limit=30)
    logger.info(f'Scanning {len(unscanned)} files into plex')
    for media in unscanned:
        manual_import(media['path'], media['library_id'], plex_session, plex_table, rimoto_table, rimoto_session, media['id'])
        sleep(10)