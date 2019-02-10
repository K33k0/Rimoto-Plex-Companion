import logging
import os
import subprocess
from time import sleep

from flask import Flask
from flask import request

base_rclone_media_path = "C:/Media"
remote_mount_folder_name = "gcache"

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)


@app.route("/")
def hello_world():
    return "Hello World!"


@app.route("/scan", methods=["POST"])
def scan():
    if "anime" in os.path.dirname(request.form["folder"]):
        section = "3"
        file_path = __translate_file_path(request.form["folder"])
        __wait_for_path(file_path)

    elif "Adult" in os.path.dirname(request.form["folder"]):
        section = "11"
        file_path = __translate_file_path(request.form["folder"])
        __wait_for_path(file_path)

    elif "Family" in os.path.dirname(request.form["folder"]):
        section = "13"
        file_path = __translate_file_path(request.form["folder"])
        __wait_for_path(file_path)

    elif "Kids" in os.path.dirname(request.form["folder"]):
        section = "12"
        file_path = __translate_file_path(request.form["folder"])
        __wait_for_path(file_path)

    elif "Movies" in os.path.dirname(request.form["folder"]):
        section = "2"
        file_path = __translate_file_path(request.form["folder"])
        __wait_for_path(file_path)
    else:
        return "False"

    result = subprocess.Popen(
        f'"E:/Utils/Plex/Plex Media Scanner.exe" -c {section} -s -r --no-thumbs -d "{file_path}"',
        stdout=subprocess.PIPE,
    )
    while result.poll() is None:
        sleep(5)
    return f"Success: {file_path}"


def __wait_for_path(path):
    p = path
    p = p.replace('"', "")
    while not os.path.isfile(p):
        logging.debug(f"Path does not exist: {path}")
        sleep(5)
    return os.path.isfile(p)


def __translate_file_path(folder):
    base = base_rclone_media_path
    r_base = remote_mount_folder_name
    stripped_remote_path = folder.split(r_base)[1]
    file_path = base + stripped_remote_path
    logging.debug(f"Translated_file_path: {file_path}")
    return file_path


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
