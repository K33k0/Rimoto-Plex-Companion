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


base_rclone_media_path = cfg.base_rclone_media_path
remote_mount_folder_name = cfg.remote_mount_folder_name
logfile = cfg.logfile_path
plex_scanner_path = cfg.plex_scanner_path
minutes_check_for_path_existence = cfg.minutes_between_scanner_checks

logzero.logfile(logfile, maxBytes=4028)

path_keys = cfg.media_path_keys


class Scanner:
    def __init__(self, interval=60):
        self.interval = interval
        self.thread = threading.Thread(target=self.main, args=())
        self.thread.daemon = True
        self.thread.start()
        logger.info(f"Initialized scanner {self.thread.ident}")

    def get_media_category(self, remote_file_path):
        """Loop through path keys and compare to path to generate category."""
        logger.debug(f'Finding category for {remote_file_path}')
        for key, section in path_keys:
            if key in os.path.dirname(remote_file_path):
                logger.debug(
                    f"Media Category for {remote_file_path} is {key}-{section}"
                )
                return section
            else:
                continue
        else:
            logger.warning(f'Failed to find category')

    def remote_file_to_local_file(self, remote_file_path):
        """Convert remote path to local path."""
        file_path = (
            base_rclone_media_path + remote_file_path.split(remote_mount_folder_name)[1]
        )
        local_file_path = PureWindowsPath(file_path)
        logger.debug(f"converted remote path to {local_file_path}")
        return local_file_path

    def wait_path(self, windows_file_path):
        """Wait for the path to be available within windows."""
        path_exists = Path(windows_file_path).exists()
        if path_exists:
            logger.debug(f'Local file found {windows_file_path}')
            return True
        else:
            return False

    def import_to_plex(self, windows_folder_path: Path, section):
        """Run the plex scanner until file is within the db."""
        if not Path(windows_folder_path).is_dir():
            return False
        # Only runs if path is verified
        result = subprocess.Popen(
            f'"{plex_scanner_path}" -c {section} -s -r --no-thumbs -d "{windows_folder_path}"'
        )  # nosec;
        while result.poll() is None:
            # Wait for scanner to finish
            sleep(10)
        return True

    def verify_import_in_db(self, windows_file_path: PureWindowsPath):
        """Check db for filepath and return the plex record."""
        db_result = MediaParts.query.filter_by(file=str(windows_file_path)).first()
        if not db_result:
            logger.warning(f"Failed to import path - {windows_file_path}")
            return False
        else:
            logger.debug(f"Verified import: True, Plex_id: {db_result.id}")
            response = dict(id=db_result.id, file=db_result.file)
            return response

    def fetch_awaiting_scan(self):
        """Find all records that need scanning."""
        records = Media.query.filter(
            (Media.downloaded_at > Media.scanned_at) | (Media.scanned_at.is_(None))
        ).all()
        return records

    def main(self):
        """Periodically loop through the database scanning any available media."""
        while True:
            for rec in self.fetch_awaiting_scan():
                category = self.get_media_category(rec.path)
                local_path = self.remote_file_to_local_file(rec.path)
                local_path_existence = self.wait_path(local_path)
                if not local_path_existence:
                    continue
                self.import_to_plex(Path(local_path).parent, category)
                local_file_imported = self.verify_import_in_db(local_path)
                if local_file_imported:
                    rec.scanned_at = dt.now()
                    if not rec.scan_attempts:
                        rec.scan_attempts = 1
                    else:
                        rec.scan_attempts += 1
                    model.db.session.commit()
            sleep(30)


scanner_task = Scanner()
scanner_data = {
    'id': scanner_task.thread.ident,
    'is_alive' : scanner_task.thread.is_alive()
}
