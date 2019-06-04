def count_all_records(session,table):
    return session.query(table).count()

def list_unscanned(session,table,limit=20):
    rows = session.query(table).filter((
        table.downloaded_at > table.scanned_at
    ) | (
        table.scanned_at.is_(None)
    )).all()

    return [{
        'id':row.id,
        'path':row.path,
        'downloaded_at':row.downloaded_at,
        'scanned_at':row.scanned_at,
        'version_number':row.version_number,
        'scan_attempts':row.scan_attempts,
    } for row in rows]        

def list_recently_scanned(session, table, limit=20):
    rows = session.query(table).order_by(table.scanned_at.desc()).limit(limit)
    return [{
        'id':row.id,
        'path':row.path,
        'downloaded_at':row.downloaded_at,
        'scanned_at':row.scanned_at,
        'version_number':row.version_number,
        'scan_attempts':row.scan_attempts,
    } for row in rows]

def delete_from_queue(session, table, path):
    session.query(table).filter_by(path=path).delete()
    session.commit()

def add_to_queue(session, table, path):
    row = table(path=path)
    session.add(row)
    session.commit()

        