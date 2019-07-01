from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker, scoped_session


engine = create_engine('sqlite:///C:/.plex/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db')
metadata = MetaData()
metadata.reflect(engine, only=['media_parts'])
Base = automap_base(metadata=metadata)
Base.prepare()
Plex = Base.classes.media_parts

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
