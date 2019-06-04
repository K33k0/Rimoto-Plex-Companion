from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime as dt

engine = create_engine('sqlite:///C:/.plex/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db')
metadata = MetaData()
metadata.reflect(engine, only=['media_parts'])
Base = automap_base(metadata=metadata)
Base.prepare()
Plex = Base.classes.media_parts

Session = sessionmaker(bind=engine)

    