from datetime import datetime as dt
from os import getenv

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session


engine = create_engine(getenv('RIMOTO_DB'))
Base = declarative_base()


class Media(Base):
    __tablename__ = 'Media'
    id = Column(Integer, primary_key=True)
    vps_path = Column(String(300), nullable=False)
    plex_library_id = Column(Integer, nullable=False)
    date_added = Column(DateTime, default=dt.now)
    plex_id = Column(Integer, nullable=True)
    server_path = Column(String(300), nullable=False)
    date_scanned = Column(DateTime, nullable=True)


Base.metadata.create_all(engine)
SESSION_FACTORY = sessionmaker(bind=engine)
Session = scoped_session(SESSION_FACTORY)
