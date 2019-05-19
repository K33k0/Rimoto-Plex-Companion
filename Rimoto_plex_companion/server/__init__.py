"""The code behind the server, including the routes and socketio stuff."""
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
from logzero import logger

app = Flask(__name__)
socketio = SocketIO(app)

from Rimoto_plex_companion import model # noqa; ignore import not at top. Required for flask


@app.route('/')
def index():
    """Render the index template and serve."""
    return render_template('index.html')


@app.route("/scan", methods=['POST'])
@app.route("/queue/add", methods=['POST'])
def add_to_queue_path():
    """Submit a selected path for addition to the scan queue."""
    path = request.form['file_path']
    logger.debug(f'Adding path to queue: {path}')
    return jsonify(model.add_to_queue(path))


@app.route('/queue')
@app.route('/queue/view')
def view_queue_path():
    """Render the queue template and serve."""
    queue = model.view_queue()
    return render_template('queue.html', queue=queue)


@socketio.on('delete path from queue')
def delete_from_queue(data):
    """Route to remove selected path from queue."""
    return model.delete_from_queue(data['data'])


@app.route('/added')
def view_recently_added():
    """Route for recently media recenlty scanned in to plex."""
    items = model.recent_added()
    return render_template('added.html', items=items)
