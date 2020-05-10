from app import app, db
from app.forms import LoginForm, RegistrationForm, EditNoteForm
from app.models import User, Note
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('login'))
		login_user(user)
		return redirect(url_for('index'))
	return render_template('login.html', form=form)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, email=form.email.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Created new user: {}'.format(form.username.data))
		return redirect(url_for('login'))
	return render_template('register.html', form=form)

@app.route('/<username>/notes', methods=['GET', 'POST'])
@login_required
def notes(username):
	note_id = request.args.get('note_id', None, type=int)
	edit_flag = request.args.get('edit_flag', False, type=bool)
	del_flag = request.args.get('del_flag', False, type=bool)

	user = User.query.filter_by(username=username).first()
	notes = user.notes.order_by(Note.update_time.desc()).all()

	form = EditNoteForm()

	if form.validate_on_submit():
		if edit_flag == True and note_id is None:
		# create new note
			note = Note(title=form.title.data, body=form.body.data, user_id=user.id)
			db.session.add(note)
			db.session.commit()
			flash('Created new note. Title: {}'.format(note.title))
			return redirect(url_for('notes', username=current_user.username))
		elif edit_flag == True and note_id is not None:
		# edit note
			note = user.notes.filter_by(id=note_id).first()
			if note is not None:
				if note.title != form.title.data or note.body != form.body.data:
					note.title = form.title.data
					note.body = form.body.data
					note.update_time = datetime.utcnow()
					db.session.commit()
					flash('Saved changes to note. Title: {}'.format(note.title))
				else:
					flash('There is no change provided')
			else:
				flash('No data found')
			return redirect(url_for('notes', username=current_user.username))
		else:
			return redirect(url_for('notes', username=current_user.username))
	elif request.method == 'GET' and note_id is not None and edit_flag == True:
	# prepare form of selected note
		note = user.notes.filter_by(id=note_id).first()
		if note is not None:
			form.title.data = note.title
			form.body.data = note.body
		else:
			return redirect(url_for('notes', username=current_user.username))

	return render_template(
		'notes.html',
		form=form,
		notes=notes,
		note_id=note_id,
		edit_flag=edit_flag,
		del_flag=del_flag)

@app.route('/del_note/<note_id>')
@login_required
def del_note(note_id):
	note = current_user.notes.filter_by(id=note_id).first()
	if note is not None:
		flash('Deleted note: {}'.format(note.title))
		db.session.delete(note)
		db.session.commit()
	else:
		flash('No data found')
	return redirect(url_for('notes', username=current_user.username))
