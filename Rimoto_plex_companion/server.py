import os
import sqlite3
import subprocess
from pathlib import Path, PureWindowsPath
from time import sleep

from datetime import datetime as dt

import logzero
from logzero import logger

from rimoto_plex_companion.db_init import Media, Session

app = Flask(__name__)
logfile = "I:/Logs/Rimoto/inbound.log"
logzero.logfile(logfile, maxBytes=4028)
session = Session()





def main():
    app.run(port=5000, debug=True)
    session.close()


if __name__ == "__main__":
    main()




