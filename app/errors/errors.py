from app import db
from flask import Blueprint, render_template

errors_bp = Blueprint('errors_bp', __name__, template_folder='templates')


@errors_bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@errors_bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500
