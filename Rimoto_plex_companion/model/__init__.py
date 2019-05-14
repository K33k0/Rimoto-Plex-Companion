from datetime import datetime as dt
import pathlib
import os
from flask_sqlalchemy import SQLAlchemy
from logzero import logger

from Rimoto_plex_companion.server import app

app.config['SQLALCHEMY_DATABASE_URI'] =  'sqlite:///C:/.plex/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db'
app.config['SQLALCHEMY_BINDS'] = {
        'rimoto':'sqlite:///rimoto.db'
    }
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
db = SQLAlchemy(app)


def add_to_queue(path):
    start = Media.query.count()
    row = Media(path=path)
    db.session.add(row)
    end = Media.query.count()
    total_added = end - start
    logger.info(f'Added {end - start} record(s)')
    db.session.commit()
    data = {'path': path, 'date_added': dt.now(), 'total_records': end, 'total_added': total_added}
    return data

def view_queue():
    rows = Media.query.filter_by(scanned_at=None).all()
    return rows

def recent_added():
    rows = Media.query.order_by(Media.scanned_at.desc()).limit(50)
    return rows

class Media(db.Model):
    __bind_key__ = 'rimoto'
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(300))
    downloaded_at = db.Column(db.DateTime, default=dt.now)
    scanned_at = db.Column(db.DateTime)
    version_num = db.Column(db.Integer)
    scan_attempts = db.Column(db.Integer)

    def __repr__(self):
        return f'path: {self.path}, downloaded at: {self.downloaded_at}, scanned at: {self.scanned_at}'

class MediaParts(db.Model):
    __table_args__ = {
        'autoload': True,
        'autoload_with': db.engine
    }

db.create_all()
