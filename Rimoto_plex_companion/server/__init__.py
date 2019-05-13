from flask import Flask, request


@app.route("/scan", methods=['POST'])
def scan_post():
    media = Media()
    start = session.query(Media).count()
    media.path = request.form.get('file_path')
    media.downloaded_at = dt.strptime(request.form.get('timestamp'), "%Y-%m-%d %H:%M:%S.%f")
    session.add(media)
    end = session.query(Media).count()
    logger.info(f'Added {end - start} record(s)')
    return f'Added {end - start} record(s)'

def scan(path:, )