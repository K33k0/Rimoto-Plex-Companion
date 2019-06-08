from datetime import datetime as dt

import hug
from hug.middleware import CORSMiddleware

from Model.rimoto_db import Rimoto, Session as r_session
from Model.plex_db import Plex, Session as p_session
from Model.selections import count_all_records, list_unscanned, list_recently_scanned, add_to_queue, delete_from_queue, manual_import, scan_all
from Rimoto_plex_companion.tasks.scanner import Scanner



api = hug.API(__name__)
api.http.add_middleware(CORSMiddleware(api))

@hug.get('/queue')
def show_queue():
    session = r_session()
    return list_unscanned(session, Rimoto)


@hug.get('/recent')
def get_recent():
    session = r_session()
    return list_recently_scanned(session, Rimoto)


@hug.post('/scan')
def new_path(file_path: hug.types.text):
    session = r_session()
    print(f'Added { file_path } to queue')
    add_to_queue(session, Rimoto, file_path)


@hug.post('/delete')
def delete_path(file_path: hug.types.text):
    session = r_session()
    delete_from_queue(session, Rimoto, file_path)

@hug.post('/manualscan')
def scan(path, section_id, record_id):
    # plex_session, plex_table, rim_table, rim_session
    plex_session = p_session()
    rimoto_session = r_session()
    plex_table = Plex
    rimoto_table = Rimoto
    manual_import(path, section_id, plex_session, plex_table, rimoto_table, rimoto_session, record_id)

@hug.get('/scan_all')
def scan_all_unscanned():
    print('Response will likely timeout')
    plex_session = p_session()
    rimoto_session = r_session()
    plex_table = Plex
    rimoto_table = Rimoto
    scan_all(plex_session, plex_table, rimoto_session, rimoto_table)
    return 'Scanner initialized'
