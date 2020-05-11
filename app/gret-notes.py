from app import app, db
from app.models import User, Note, Tag, note_tag

@app.shell_context_processor
def make_shell_context():
	return {
		'db': db,
		'User': User,
		'Note': Note,
		'Tag': Tag,
		'note_tag': note_tag
	}

