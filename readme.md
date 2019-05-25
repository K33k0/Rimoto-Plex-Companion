- Rclone hitting your gdrive api limit?

- Plex taking for ever to scan in that one episode from your download stack?

- Countless problems because your plex server is not the same as your download server?

# Rimoto Plex Companion
## To The Rescue!

I've got a download vps that connects up to google drive, and I have my plex server running locally connected up to my vps.

Once a download is finished within Sonarr or Radarr, it sends a post request to rimoto on your local plex box. Which is then stored in local database. The built in rimoto scanner will periodically loop through your database, check your rclone mount location for the files existence and scan it into plex!

All config is done within config.py

`base_rclone_media_path`: This is the root of your remote media directory
- For example `mount gcache:/Media Z:` so base_rclone_media_path would be `Z:/Media`

`remote_mount_folder_name`: The VPS folder name where your media is
- VPS Media is mounted at `/mnt/gcache/` so config would be `'gcache'`

`logfile_path`: Where to put your logs
- Example `I:/Logs/Rimoto/scanner.log`

`plex_scanner_path`: Location of `plex media scanner.exe`
- `'C:/Plex/Plex Media Scanner.exe'`

`media_path_keys`: An list of tuples that containing a reference to each of your libraries `("unique folder path", "Plex library number")`,

- Example. Two paths within gcache /Media/TV, /Media/Movies. plex library number for TV is 1 and Movies library number is 2.
- This would result in code looking like this `[('TV','1'), ('Movies',2)]`

`minutes_between_scanner_checks`: Simply how many minutes between loops of the database
- for example: 1

`serve_on_port`: The port to run your plex server on
- for example: 5000

`server_debug`: Whether to run your server in debug mode or not. I recommend not

- for example: False

`plex_library_db_connection_string`: the location of plex's database containing your media. 
- for example: `"sqlite:///C:/.plex/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db"`

`rimoto_db_connection_string`: Connection string tou your rimoto db
- I recommend ` "sqlite:///rimoto.db"`

`db_track_modifications`: Not sure what it does but sqlalchemy complains when it's on
- Looks a bit messy so Set to False

`db_echo`:Displays the sql output
- Looks a bit messy so Set to False

`secret_key`: Secret key to your app. WTFForms wont work without it
- example `"skfd908u8234kansdvoij"`


