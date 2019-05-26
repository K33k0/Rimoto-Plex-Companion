# TODO: Rename variables to a readable form
# TODO: Comment any code that isn't straight forward
# TODO: Take a look into splitting the code into smaller modules. Eg- DB,View_models, Forms etc
"""Contains all db declarations and models for RPC."""
from datetime import datetime as dt
from flask_sqlalchemy import SQLAlchemy
from logzero import logger
from flask_wtf import FlaskForm
from wtforms import StringField, FileField, IntegerField
from wtforms.validators import DataRequired, regexp

from Rimoto_plex_companion.server import app
from Rimoto_plex_companion import config as cfg


app.config["SQLALCHEMY_DATABASE_URI"] = cfg.plex_library_db_connection_string
app.config["SQLALCHEMY_BINDS"] = {"rimoto": cfg.rimoto_db_connection_string}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = cfg.db_track_modifications
app.config["SQLALCHEMY_ECHO"] = cfg.db_echo
app.config["SECRET_KEY"] = cfg.secret_key
db: SQLAlchemy = SQLAlchemy(app)


def add_to_queue(path):
    """Add selected path to the queue."""
    start = Media.query.count()
    row = Media(path=path)
    db.session.add(row)
    end = Media.query.count()
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


def get_queue():
    """Return all rows from sql db that have no 'scanned at' value."""
    rows = Media.query.filter((Media.downloaded_at > Media.scanned_at) | (Media.scanned_at.is_(None))).all()
    return rows


def recent_added(total_records=50):
    """Return x most recent rows from db."""
    rows = Media.query.order_by(Media.scanned_at.desc()).limit(total_records)
    return rows


def delete_from_queue(path):
    """Delete path from database."""
    Media.query.filter_by(path=path).delete()
    db.session.commit()


class Media(db.Model):
    """Media table for rimoto from local db."""

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
    """Media table from main plex db. Which is auto generated."""

    __table_args__ = {"autoload": True, "autoload_with": db.engine}


class AddToQueue(FlaskForm):
    path = StringField("path", validators=[DataRequired()])


db.create_all()
