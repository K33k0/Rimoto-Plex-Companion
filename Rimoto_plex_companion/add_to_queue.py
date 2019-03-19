import requests
import os
from datetime import datetime as dt
from logzero import logger


def sonarr():
    url = "https://home.k33k00.com/scan"
    episode_path = os.environ["sonarr_episodefile_path"]
    logger.info(f"Sending {episode_path} to server")
    r = requests.post(url, data={
        "file_path": episode_path,
        "timestamp": dt.utcnow()
    })

def radarr():
    url = "https://home.k33k00.com/scan"
    movie_path = os.environ["radarr_moviefile_path"]
    logger.info(f"Sending {movie_path} to server")
    r = requests.post(url, data={
        "file_path": movie_path,
        "timestamp": dt.utcnow()
    })