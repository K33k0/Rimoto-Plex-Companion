from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

index_route = Blueprint('index_route', __name__)

@index_route.route('/')
def show():
    try:
        return render_template('index.html')
    except TemplateNotFound:
        abort(404)