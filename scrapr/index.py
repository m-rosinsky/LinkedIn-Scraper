from flask import (
    Blueprint, request,
)

bp = Blueprint('index', __name__)

@bp.route('/', methods=('GET',))
def index():
    return 'hello'
