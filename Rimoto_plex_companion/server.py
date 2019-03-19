import os
import sqlite3
import subprocess
from pathlib import Path, PureWindowsPath
from time import sleep

from tinydb import TinyDB
import hug
import logzero
from logzero import logger

db = TinyDB("db.json", sort_keys=True, indent=4, separators=(',', ': '))
table = db.table('inbound')
logfile = "I:/Logs/Rimoto/inbound.log"

logzero.logfile(logfile, maxBytes=4028)

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
    if isinstance(remote_file_path,list):
        remote_file_path = ','.join(remote_file_path)
    logger.info(f"Request from {request.headers['X-REAL-IP']} to {remote_file_path}")
    result = table.insert({'remote_path': remote_file_path})
    return result

@hug.post("/scan")
def scan_post(body):
    result = table.insert(
        {
        "remote_path": body["file_path"],
         "timestamp": body["timestamp"] 
         }
        )
    return result



def main():
    hug.development_runner._start_api(__name__, "127.0.0.1", 5000, True, show_intro=True)

if __name__ == "__main__":
    main()