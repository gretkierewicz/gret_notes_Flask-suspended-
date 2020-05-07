from app import app, db
from app.forms import LoginForm, RegistrationForm, EditNoteForm
from app.models import User, Note
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

@app.route('/notes', methods=['GET', 'POST'])
@login_required
def notes():
	note_id = request.args.get('note', None, type=int)
	user = User.query.filter_by(username=current_user.username).first()
	notes = user.notes.order_by(Note.timestamp.desc()).all()
	form = EditNoteForm()
	if note_id is not None:
		edited_note = user.notes.filter_by(id=note_id).first()
		if edited_note is not None:
			form.title.data = edited_note.title
			form.body.data = edited_note.body
		else:
			return redirect(url_for('notes'))
	if form.validate_on_submit():
		note = Note(title=form.title.data, body=form.body.data, user_id=user.id)
		db.session.add(note)
		db.session.commit()
		flash('Created new note. Title: {}'.format(form.title.data))
		return redirect(url_for('notes'))
	return render_template('notes.html', user=user, form=form, notes=notes)
