import hug
from hug.middleware import CORSMiddleware

from Model.rimoto_db import Rimoto, Session as r_session
from Model.plex_db import Plex, Session as p_session
from Model.selections import count_all_records, list_unscanned, list_recently_scanned, add_to_queue, delete_from_queue

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
def new_path(body):
    session = r_session()
    print(f'Added { body["file_path"] } to queue')
    add_to_queue(session, Rimoto, body['file_path'])

@hug.post('/delete')
def delete_path(body):
    session = r_session()
    delete_from_queue(session, Rimoto, body['path'])


