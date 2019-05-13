from pathlib import Path, PureWindowsPath

from app import __read_db
from app import __scan
from app import __translate_file_path
from app import __verify_import
from app import __wait_for_path


def test_path_wait_for_path():
    test_path = "C:/Media/TV/Family/Brooklyn Nine-Nine/Season 1/Brooklyn Nine-Nine - S01E01 - Pilot WEBDL-1080p.mp4"
    test_path = Path(test_path)
    assert __wait_for_path(test_path) is True


def test_translate_path():
    test_path = "/home15/r0v51jiozjqo/gcache/Anime/Black Clover/Season 1/Black Clover - S01E72 - St. Elmo’s Fire HDTV-1080p.mkv"
    assert str(__translate_file_path(test_path)) == "C:\\Media\\Anime\\Black Clover\\Season 1\\Black Clover - S01E72 - St. Elmo’s Fire HDTV-1080p.mkv"


def test_read_db():
    test_path = "C:\\Media\\TV\\Family\\Brooklyn Nine-Nine\\Season 1\\Brooklyn Nine-Nine - S01E01 - Pilot WEBDL-1080p.mp4"
    assert __read_db(test_path) is not None


def test_scan():
    test_path = "C:\\Media\\TV\\Family\\Brooklyn Nine-Nine\\Season 1\\Brooklyn Nine-Nine - S01E01 - Pilot WEBDL-1080p.mp4"
    test_path = PureWindowsPath(test_path)
    assert __scan(test_path, 13) is True


def test_verify():
    test_path = "/home15/r0v51jiozjqo/gcache/Anime/Black Clover/Season 1/Black Clover - S01E72 - St. Elmo’s Fire HDTV-1080p.mkv"
    assert __verify_import(test_path) is not False