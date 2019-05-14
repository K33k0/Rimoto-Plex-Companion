from Rimoto_plex_companion.server import app


def main():
    app.run(port=5000, debug=True)


if __name__ == "__main__":
    main()