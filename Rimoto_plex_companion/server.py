"""Run the server."""
from Rimoto_plex_companion import config as cfg
from Rimoto_plex_companion.server import socketio, app  # type: ignore



def main():
    """Server the app."""
    socketio.run(app, port=cfg.serve_on_port, debug=cfg.server_debug)


if __name__ == "__main__":
    main()
