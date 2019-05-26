# TODO: Rename variables to a readable form
# TODO: Comment any code that isn't straight forward
# TODO: See if there is a way to make a route simply return a render template
# TODO: Anything that doesn't return a template is technically an api call. Make them!
# TODO: Split API, socket calls etc into seperate models
"""The code behind the server, including the routes and socketio stuff."""
from flask import Flask, render_template, jsonify, request, redirect
from flask_socketio import SocketIO
from logzero import logger


app = Flask(__name__)
socketio = SocketIO(app)

from Rimoto_plex_companion import (
    model,
    tasks,
)  # noqa; ignore import not at top. Required for flask


@app.route("/")
def index():
    """Render the index template and serve."""
    return render_template("index.html")


@app.route("/scan", methods=["POST"])
@app.route("/queue/add", methods=["POST"])
def add_to_queue_path():
    """Submit a selected path for addition to the scan queue."""
    try:
        path = request.form["file_path"]
        return jsonify(model.add_to_queue(path))

    except KeyError:
        path = request.form["path"]
        model.add_to_queue(path)
        return redirect("/queue")

    logger.info(f"Adding path to queue: {path}")


@app.route("/queue", methods=("GET", "POST"))
@app.route("/queue/view", methods=("GET", "POST"))
def view_queue_path():
    """Render the queue template and serve."""
    form = model.AddToQueue()
    if form.validate_on_submit():
        return redirect("/queue")
    queue = model.view_queue()
    return render_template("queue.html", queue=queue, form=form)


@socketio.on("delete path from queue")
def delete_from_queue(data):
    """Route to remove selected path from queue."""
    return model.delete_from_queue(data["data"])


@app.route("/added")
def view_recently_added():
    """Route for recently media recenlty scanned in to plex."""
    items = model.recent_added()
    return render_template("added.html", items=items)


@app.route("/settings")
def view_settings():
    return render_template("config.html", settings=tasks.scanner_data)
