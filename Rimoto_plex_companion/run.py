from datetime import datetime as dt
import os
from pathlib import Path, PureWindowsPath
import subprocess
import threading
import time
from time import sleep

from flask import Flask, render_template, jsonify, request, redirect
from flask_wtf import FlaskForm
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from logzero import logger
import requests
from wtforms import StringField, FileField, IntegerField
from wtforms.validators import DataRequired, regexp

from Rimoto_plex_companion import config as cfg

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = cfg.plex_library_db_connection_string
app.config["SQLALCHEMY_BINDS"] = {"rimoto": cfg.rimoto_db_connection_string}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = cfg.db_track_modifications
app.config["SQLALCHEMY_ECHO"] = cfg.db_echo
app.config["SECRET_KEY"] = cfg.secret_key
db = SQLAlchemy(app)
socketio = SocketIO(app)

from Rimoto_plex_companion.routes import index_route

app.register_blueprint(index_route)

# VIEWS
# @app.route("/")
# def index():
#     """Render the index template and serve."""
#     logger.debug('Serving index')
#     return render_template("index.html")


@app.route("/scan", methods=["POST"])
@app.route("/queue/add", methods=["POST"])
def add_to_queue_path():
    """Submit a selected path for addition to the scan queue."""

    try:
        path = request.form["file_path"]
        return jsonify(Model.add_to_queue(path))

    except KeyError:
        path = request.form["path"]
        Model.add_to_queue(path)
        return redirect("/queue")

    logger.info(f"Adding path to queue: {path}")


@app.route("/queue", methods=("GET", "POST"))
@app.route("/queue/view", methods=("GET", "POST"))
def view_queue_path():
    """Render the queue template and serve."""

    form = Forms.AddToQueue()
    if form.validate_on_submit():
        return redirect("/queue")
    queue = Model.get_queue()
    return render_template("queue.html", queue=Model.get_queue(), form=form)


@socketio.on("delete path from queue")
def delete_from_queue(data):
    """Route to remove selected path from queue."""
    Model.delete(data)
    return


@app.route("/added")
def view_recently_added():
    """Route for recently media recenlty scanned in to plex."""
    items = Model.recently_added()
    return render_template("added.html", items=items)


@app.route("/settings")
def view_settings():
    return render_template("config.html", settings=scanner_data)


class Model:
    class Media(db.Model):
        __bind_key__ = "rimoto"
        id = db.Column(db.Integer, primary_key=True)
        path = db.Column(db.String(300))
        downloaded_at = db.Column(db.DateTime, default=dt.now)
        scanned_at = db.Column(db.DateTime)
        version_num = db.Column(db.Integer)
        scan_attempts = db.Column(db.Integer)

        def __repr__(self):
            """Print a human readable response of Media table."""
            return f"path: {self.path}, downloaded_at: {self.downloaded_at}, scanned_at: {self.scanned_at}"
    class MediaParts(db.Model):
        __table_args__ = {"autoload": True, "autoload_with": db.engine}
    
    @staticmethod
    def get_queue():
        rows = Model.Media.query.filter((Model.Media.downloaded_at > Model.Media.scanned_at) | (Model.Media.scanned_at.is_(None))).all()
        return rows

    @staticmethod
    def recently_added():
        return Model.Media.query.order_by(Model.Media.scanned_at.desc()).limit(50)

    @staticmethod
    def delete(path):
        Media.query.filter_by(path=path).delete()
        db.session.commit()

    @staticmethod
    def add_to_queue(path):
        start = Model.Media.query.count()
        row = Model.Media(path=path)
        db.session.add(row)
        end = Model.Media.query.count()
        total_added = end - start
        logger.info(f"Added {end - start} record(s)")
        db.session.commit()
        data = {
            "path": path,
            "date_added": dt.now(),
            "total_records": end,
            "total_added": total_added,
        }
        return data


class Forms:
    class AddToQueue(FlaskForm):
        path = StringField("path", validators=[DataRequired()])


db.create_all()


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
        db_result = Model.MediaParts.query.filter_by(file=str(windows_file_path)).first()
        if db_result:
            return dict(id=db_result.id, file=db_result.file)
        return False

    
    def update_db(self, record):
        if not record.scan_attempts:
            record.scan_attempts = 0
        record.scanned_at = dt.now()
        record.scan_attempts += 1
        db.session.commit()


    def main(self):
        """Periodically loop through the database scanning any available media."""
        while True:
            for rec in Model.Media.query.filter((Model.Media.downloaded_at > Model.Media.scanned_at) | (Model.Media.scanned_at.is_(None))).all():
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


scanner_task = Scanner()
scanner_data = {
    'id': scanner_task.thread.ident,
    'is_alive' : scanner_task.thread.is_alive()
}


if __name__ == "__main__":
    socketio.run(app, port=cfg.serve_on_port, debug=cfg.server_debug)
