"""API and entrypoint to rimoto."""
import threading
import time

import hug
from hug.middleware import CORSMiddleware
from logzero import logger

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


def start_tasks():
    """"""
    next_call = time.time()
    while True:
        scan_all()
        try:
            next_call += 10
            time.sleep(next_call - time.time())
        except ValueError:
            time.sleep(10)
            next_call = time.time()


ROUTER.get('/queue')(list_unscanned)
ROUTER.get('/recent')(list_recently_scanned)
ROUTER.post('/scan')(add_to_queue)
ROUTER.post('/delete')(delete_from_queue)
ROUTER.post('/manualscan')(manual_import)
ROUTER.get('/scan_all')(scan_all)


def main():
    """"""
    timer_thread = threading.Thread(target=start_tasks)
    timer_thread.daemon = True
    timer_thread.start()
    hug.development_runner.hug(module=__name__, host='127.0.0.1', port=8000)
