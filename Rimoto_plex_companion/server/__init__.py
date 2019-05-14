from flask import Flask, render_template
from flask import jsonify
from flask import request
app = Flask(__name__)
from Rimoto_plex_companion import model




@app.route("/scan", methods=['POST'])
@app.route("/queue/add", methods=['POST'])
def add_to_queue_path():
    path = request.form['file_path']
    return jsonify(model.add_to_queue(path))

@app.route('/queue')
@app.route('/queue/view')
def view_queue_path():
    queue = model.view_queue()
    return render_template('queue.html', queue=queue)

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r