from flask import Blueprint


bp = Blueprint('notes_bp', __name__,
               template_folder='templates',
               static_folder='static',
               static_url_path='/notes/static')


from . import forms, routes
