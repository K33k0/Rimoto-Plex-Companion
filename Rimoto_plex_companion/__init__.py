"""API and entrypoint to rimoto."""
import threading
import time

import hug
from hug.middleware import CORSMiddleware
from logzero import logger

from Rimoto_plex_companion.Model.rimoto_db import Rimoto, Session as r_session
from Rimoto_plex_companion.Model.plex_db import Plex, Session as p_session
from Rimoto_plex_companion.Model.selections import list_unscanned
from Rimoto_plex_companion.Model.selections import list_recently_scanned
from Rimoto_plex_companion.Model.selections import add_to_queue
from Rimoto_plex_companion.Model.selections import manual_import
from Rimoto_plex_companion.Model.selections import scan_all
from Rimoto_plex_companion.Model.selections import delete_from_queue


API = hug.API(__name__)
API.http.add_middleware(CORSMiddleware(API))
ROUTER = hug.route.API(__name__)
logger.info('Starting rimoto backend server')


def show_queue():
    """"""
    logger.info('Received request for /queue')
    session = r_session()
    data = list_unscanned(session, Rimoto)
    r_session.remove()
    return data


def get_recent():
    """"""
    logger.info('Received request for /recent')
    session = r_session()
    data = list_recently_scanned(session, Rimoto)
    r_session.remove()
    return data


def new_path(file_path: hug.types.text):
    """"""
    logger.info('Received request for /scan')
    session = r_session()
    print(f'Added { file_path } to queue')
    add_to_queue(session, Rimoto, file_path)
    r_session.remove()


def delete_path(file_path: hug.types.text):
    """"""
    logger.info('Received request for /delete')
    session = r_session()
    delete_from_queue(session, Rimoto, file_path)
    r_session.remove()


def scan(path, section_id, record_id):
    """"""
    logger.info('Received request for /manualscan')
    plex_session = p_session()
    rimoto_session = r_session()
    plex_table = Plex
    rimoto_table = Rimoto
    manual_import(path, section_id, plex_session, plex_table,
                  rimoto_table, rimoto_session, record_id)
    r_session.remove()
    p_session.remove()


def scan_all_unscanned():
    """"""
    plex_session = p_session()
    rimoto_session = r_session()
    plex_table = Plex
    rimoto_table = Rimoto
    scan_all(plex_session, plex_table, rimoto_session, rimoto_table)
    r_session.remove()
    p_session.remove()
    return 'Scanner initialized'


def start_tasks():
    """"""
    next_call = time.time()
    while True:
        scan_all_unscanned()
        try:
            next_call += 300
            time.sleep(next_call - time.time())
        except ValueError:
            time.sleep(300)
            next_call = time.time()


ROUTER.get('/queue')(show_queue)
ROUTER.get('/recent')(get_recent)
ROUTER.post('/scan')(new_path)
ROUTER.post('/delete')(delete_path)
ROUTER.post('/manualscan')(scan)
ROUTER.get('/scan_all')(scan_all_unscanned)


def main():
    """"""
    timer_thread = threading.Thread(target=start_tasks)
    timer_thread.daemon = True
    timer_thread.start()
    hug.development_runner._start_api(API,
                                      '127.0.0.1',
                                      8000,
                                      False,
                                      show_intro=False)
