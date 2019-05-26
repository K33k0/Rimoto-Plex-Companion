# TODO: Rename variables to a readable form
# TODO: Comment any code that isn't straight forward
# TODO: There has to be a way to make this cleaner
import threading
import time
import os
import subprocess  # nosec; Added verification clause as protection
from pathlib import Path, PureWindowsPath
from time import sleep
from datetime import datetime as dt

import logzero
from logzero import logger

from Rimoto_plex_companion import config as cfg
from Rimoto_plex_companion import model
from Rimoto_plex_companion.model import Media
from Rimoto_plex_companion.model import MediaParts


logzero.logfile(cfg.logfile_path, maxBytes=4028)

class Scanner:

    def __init__(self, interval=cfg.minutes_between_scanner_checks):
        self.interval = interval*60
        self.thread = threading.Thread(target=self.main, args=())
        self.thread.daemon = True
        self.thread.start()


    def get_media_category(self, remote_file_path, path_keys=cfg.media_path_keys):
        """Loop through path keys and compare to path to generate category."""
        for folder_section_name, plex_library_id in path_keys:
            directory = os.path.dirname(remote_file_path)
            if folder_section_name in directory:
                return plex_library_id


    def remote_file_to_local_file(self, remote_file_path,
                                  base_media_path=cfg.base_rclone_media_path,
                                  remote_mount_folder_name=cfg.remote_mount_folder_name):
        """Convert remote path to local path."""
        universal_path = remote_file_path.split(remote_mount_folder_name)[1]
        file_path = base_media_path + universal_path
        local_file_path = PureWindowsPath(file_path)
        return local_file_path


    def wait_path(self, windows_file_path):
        """Wait for the path to be available within windows."""
        return Path(windows_file_path).exists()
 

    def import_to_plex(self, windows_folder_path: Path,
                       section, plex_scanner_path=cfg.plex_scanner_path):
        """Run the plex scanner until file is within the db."""
        if not Path(windows_folder_path).is_dir():
            return False
        command = f'"{plex_scanner_path}" -c {section} -s -r --no-thumbs -d "{windows_folder_path}"'
        result = subprocess.Popen(command)
        while result.poll() is None:
            sleep(10)
        return True


    def verify_import_in_db(self, windows_file_path: PureWindowsPath):
        """Check db for filepath and return the plex record."""
        db_result = MediaParts.query.filter_by(file=str(windows_file_path)).first()
        if db_result:
            return dict(id=db_result.id, file=db_result.file)
        return False

    
    def update_db(record):
        if not record.scan_attempts:
            record.scan_attempts = 0
        record.scanned_at = dt.now()
        record.scan_attempts += 1
        model.db.session.commit()


    def main(self):
        """Periodically loop through the database scanning any available media."""
        while True:
            for rec in model.get_queue():
                category = self.get_media_category(rec.path)
                local_path = self.remote_file_to_local_file(rec.path)
                local_path_existence = self.wait_path(local_path)
                if not local_path_existence:
                    continue
                self.import_to_plex(Path(local_path).parent, category)
                local_file_imported = self.verify_import_in_db(local_path)
                if local_file_imported:
                    self.update_db(rec)
            sleep(self.interval)


