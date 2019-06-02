from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime
from sqlalchemy.ext.automap import automap_base
from datetime import datetime as dt


def init_plex_db():
    engine = create_engine("sqlite:///C:/.plex/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db")
    database = MetaData(bind=engine)
    database.reflect(
        bind=engine, only=['media_parts']
    )
    return database

def init_rimoto_db():
    engine = create_engine("sqlite:///rimoto.db")
    database = MetaData(bind=engine)
    Table('rimoto', database, 
        Column('path', String),
        Column('downloaded_at', DateTime, default=dt.now),
        Column('scanned_at', DateTime),
        Column('version_number', Integer, default=0),
        Column('scan_attempts', Integer, default=0),
    )
    return database

tables = {
    'plex': init_plex_db(),
    'rimoto': init_rimoto_db()
}
