base_rclone_media_path = "C:/Media"
remote_mount_folder_name = 'gcache'
logfile_path = "I:/Logs/Rimoto/scanner.log"
plex_scanner_path = "E:/Utils/Plex/Plex Media Scanner.exe"
media_path_keys = [
    ("Movies", "2"),
    ("Anime", "3"),
    ("Adult", "11"),
    ("Kids", "12"),
    ("Family", "13"),
]
minutes_between_scanner_checks = 1
serve_on_port = 5000
server_debug = True
plex_library_db_connection_string = 'sqlite:///C:/.plex/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db'
rimoto_db_connection_string = 'sqlite:///rimoto.db'
db_track_modifications = False
db_echo = False