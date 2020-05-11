from app import app, db
from app.forms import LoginForm, RegistrationForm, NoteForm, NewTagForm, EditTagForm
from app.models import User, Note, Tag
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required

def edit_note_tags(tags_list, user, note):
	for tag_name in tags_list:	# look for tags to add
		tag = user.tags.filter_by(name=tag_name).first()
		if tag is None:
			tag = Tag(name=tag_name, user_id=user.id)
			note.tags.append(tag)
		else:
			if not note.is_tagged(tag):
				note.tags.append(tag)
	for tag in note.tags:		# look for tags to remove
		if not tag.name in tags_list:
			note.tags.remove(tag)

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

	form = NoteForm()

	if form.validate_on_submit():
		if edit_flag == True and note_id is None:
		# create new note
			note = Note(title=form.title.data, body=form.body.data, user_id=user.id)
			db.session.add(note)
			edit_note_tags(form.tags.data.split(), current_user, note)
			db.session.commit()
			flash('Created new note. Title: {}'.format(note.title))
			return redirect(url_for('notes', username=current_user.username))
		elif edit_flag == True and note_id is not None:
		# edit note
			note = user.notes.filter_by(id=note_id).first()
			if note is not None:
				tags = ""
				for tag in note.tags:
					tags += tag.name + " "
				if note.title != form.title.data or note.body != form.body.data or tags != form.tags.data:
					note.title = form.title.data
					note.body = form.body.data
					note.update_time = datetime.utcnow()
					edit_note_tags(form.tags.data.split(), current_user, note)
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
	# prepare form for selected note
		note = user.notes.filter_by(id=note_id).first()
		if note is not None:
			form.title.data = note.title
			form.body.data = note.body
			tags = ""
			for tag in note.tags:
				tags += tag.name + " "
			form.tags.data = tags
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

@app.route('/<username>/tags', methods=['GET', 'POST'])
@login_required
def tags(username):
	user = User.query.filter_by(username=username).first()
	order_by = request.args.get('order_by', 'name', type=str)
	tag_id = request.args.get('tag_id', None, type=int)

	new_tags_form = NewTagForm()
	edit_tag_form = EditTagForm()

	if new_tags_form.validate_on_submit():
		tag_list = new_tags_form.names.data.split()
		list_str = ''
		for tag_name in tag_list:
			if user.tags.filter_by(name=tag_name).first() is None:
				tag = Tag(name=tag_name, user_id=current_user.id)
				db.session.add(tag)
				list_str += '#' + tag_name + '; '
		if list_str != '':
			db.session.commit()
			flash('Created new tags: {}'.format(list_str))

	elif edit_tag_form.validate_on_submit():
		tag = user.tags.filter_by(id=tag_id).first()
		tag_list = edit_tag_form.name.data.split()
		if tag_list[0] is not None:
			if user.tags.filter_by(name=tag_list[0]).first()is None:
				flash('Changed tag name from {old} to {new}'.format(old=tag.name, new=tag_list[0]))
				tag.name = tag_list[0]
				#tag.timestamp = datetime.utcnow()
				db.session.commit()
				tag_id = None
			else:
				flash('There is such tag already')

	elif request.method == 'GET' and tag_id is not None:
		tag = user.tags.filter_by(id=tag_id).first()
		if tag is not None:
			edit_tag_form.name.data = tag.name

	return render_template(
		'tags.html',
		user=user,
		order_by=order_by,
		new_tags_form=new_tags_form,
		tag_id=tag_id,
		edit_tag_form=edit_tag_form
	)

@app.route('/del_tag/<tag_id>')
@login_required
def del_tag(tag_id):
	tag = current_user.tags.filter_by(id=tag_id).first()
	if tag is not None:
		flash('Deleted tag: {}'.format(tag.name))
		db.session.delete(tag)
		db.session.commit()
	else:
		flash('No data found')
	return redirect(url_for('tags', username=current_user.username))
