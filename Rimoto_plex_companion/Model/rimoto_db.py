from datetime import datetime as dt

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session


engine = create_engine('sqlite:///E:/db/rimoto.db')
Base = declarative_base()


class Rimoto(Base):
    __tablename__ = 'rimoto'
    id = Column(Integer, primary_key=True)
    remote_path = Column(String)
    library_name = Column(String)
    library_id = Column(Integer)
    path = Column(String)
    downloaded_at = Column(DateTime, default=dt.now)
    exists_locally = Column(Boolean, default=False)
    scanned_at = Column(DateTime)
    version_number = Column(Integer, default=0)
    scan_attempts = Column(Integer, default=0)


Base.metadata.create_all(engine)
SESSION_FACTORY = sessionmaker(bind=engine)
Session = scoped_session(SESSION_FACTORY)
