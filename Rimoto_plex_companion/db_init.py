from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Media(Base):
    __tablename__ = "media"

    id = Column('id', Integer, primary_key=True)
    path = Column('path', String)
    downloaded_at = Column('downloaded_at', DateTime)
    scanned_at = Column('scanned_at', DateTime)
    version_num = Column('version_num', Integer)
    scan_attempts = Column('scan_attempts', Integer)


engine = create_engine('sqlite:///rimoto.db')
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
