from flask import Blueprint


bp = Blueprint('auth_bp', __name__, template_folder='templates')


from . import forms, routes
