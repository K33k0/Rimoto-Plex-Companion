from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime as dt


engine = create_engine('sqlite:///rimoto.db')
Base = declarative_base()


class Rimoto(Base):
    __tablename__ = 'rimoto'
    id = Column(Integer, primary_key = True)
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
Session = sessionmaker(bind=engine)

# TEST
