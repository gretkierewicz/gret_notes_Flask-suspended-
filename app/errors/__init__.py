from flask import Blueprint


bp = Blueprint('errors_bp', __name__, template_folder='templates')


from . import errors
