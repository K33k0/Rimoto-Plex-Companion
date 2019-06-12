from datetime import datetime as dt
import threading
import time

import hug
from hug.middleware import CORSMiddleware
from logzero import logger

from Rimoto_plex_companion.Model.rimoto_db import Rimoto, Session as r_session
from Rimoto_plex_companion.Model.plex_db import Plex, Session as p_session
from Rimoto_plex_companion.Model.selections import logzero, count_all_records, list_unscanned, list_recently_scanned, add_to_queue, delete_from_queue, manual_import, scan_all
from Rimoto_plex_companion.tasks.scanner import Scanner
logger = logzero.logger


api = hug.API(__name__)
api.http.add_middleware(CORSMiddleware(api))
logger.info('Starting rimoto backend server')

@hug.get('/queue')
def show_queue():
    logger.info('Received request for /queue')
    session = r_session()
    data = list_unscanned(session, Rimoto)
    r_session.remove()
    return data


@hug.get('/recent')
def get_recent():
    logger.info('Received request for /recent')
    session = r_session()
    data = list_recently_scanned(session, Rimoto)
    r_session.remove()
    return data


@hug.post('/scan')
def new_path(file_path: hug.types.text):
    logger.info('Received request for /scan')
    session = r_session()
    print(f'Added { file_path } to queue')
    add_to_queue(session, Rimoto, file_path)
    r_session.remove()


@hug.post('/delete')
def delete_path(file_path: hug.types.text):
    logger.info('Received request for /delete')
    session = r_session()
    delete_from_queue(session, Rimoto, file_path)
    r_session.remove()


@hug.post('/manualscan')
def scan(path, section_id, record_id):
    # plex_session, plex_table, rim_table, rim_session
    logger.info('Received request for /manualscan')
    plex_session = p_session()
    rimoto_session = r_session()
    plex_table = Plex
    rimoto_table = Rimoto
    manual_import(path, section_id, plex_session, plex_table, rimoto_table, rimoto_session, record_id)
    r_session.remove()
    p_session.remove()



@hug.get('/scan_all')
def scan_all_unscanned():
    plex_session = p_session()
    rimoto_session = r_session()
    plex_table = Plex
    rimoto_table = Rimoto
    scan_all(plex_session, plex_table, rimoto_session, rimoto_table)
    r_session.remove()
    p_session.remove()


    return 'Scanner initialized'


def start_tasks():
    next_call = time.time()
    while True:
        scan_all_unscanned()
        try:
            next_call + 300
            time.sleep(next_call - time.time())
        except ValueError:
            time.sleep(300)
            next_call = time.time()


def main():
    timer_thread = threading.Thread(target=start_tasks)
    timer_thread.daemon = True
    timer_thread.start()
    hug.development_runner._start_api(api, '127.0.0.1', 8000, False, show_intro=False)



