from datetime import datetime as dt
import os
from pathlib import Path, PureWindowsPath
import subprocess
import threading
import time
from time import sleep



base_rclone_media_path = "C:/Media"
media_path_keys = [
    ("Movies", "2"),
    ("Anime", "3"),
    ("Adult", "11"),
    ("Kids", "12"),
    ("Family", "13")]
remote_mount_folder_name = "gcache"
plex_scanner_path = "E:/Utils/Plex/Plex Media Scanner.exe"


class Scanner:

    def __init__(self, interval=1):
        self.interval = interval*60
        self.thread = threading.Thread(target=self.main, args=())
        self.thread.daemon = True
        self.thread.start()


    def get_media_category(self, remote_file_path, path_keys=media_path_keys):
        """Loop through path keys and compare to path to generate category."""
        for folder_section_name, plex_library_id in path_keys:
            directory = os.path.dirname(remote_file_path)
            if folder_section_name in directory:
                return plex_library_id


    def remote_file_to_local_file(self, remote_file_path,
                                  base_media_path=base_rclone_media_path,
                                  remote_mount_folder_name=remote_mount_folder_name):
        """Convert remote path to local path."""
        universal_path = remote_file_path.split(remote_mount_folder_name)[1]
        file_path = base_media_path + universal_path
        local_file_path = PureWindowsPath(file_path)
        return local_file_path


    def wait_path(self, windows_file_path):
        """Wait for the path to be available within windows."""
        return Path(windows_file_path).exists()
 

    def import_to_plex(self, windows_folder_path: Path,
                       section, plex_scanner_path=plex_scanner_path):
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
        session = self.plex_session()
        db_result = session.query(self.plex_table).filter(
            self.plex_table.file==str(windows_file_path)).first()
        if db_result:
            return dict(id=db_result.id, file=db_result.file)
        return False

    
    def update_db(self, record, session):
        if not record.scan_attempts:
            record.scan_attempts = 0
        record.scanned_at = dt.now()
        record.scan_attempts += 1
        session.commit()


    def get_unscanned(self, session):
        return session.query(self.rimoto_table).filter(
            (self.rimoto_table.downloaded_at > self.rimoto_table.scanned_at) | (
            self.rimoto_table.scanned_at.is_(None))
        ).all()


    def main(self):
        """Periodically loop through the database scanning any available media."""

        while True:
            rimoto_session = self.rimoto_session()
            
            for rec in self.get_unscanned(rimoto_session):
                category = self.get_media_category(rec.path)
                local_path = self.remote_file_to_local_file(rec.path)
                local_path_existence = self.wait_path(local_path)
                
                if not local_path_existence:
                    continue
                self.import_to_plex(Path(local_path).parent, category)
                local_file_imported = self.verify_import_in_db(local_path)
                
                if local_file_imported:
                    self.update_db(rec, rimoto_session)

            rimoto_session.close()
            rimoto_session = None
            sleep(self.interval)


