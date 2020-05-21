from app import app, db
from app.forms import LoginForm, RegistrationForm, NoteForm, NewTagForm, EditTagForm
from app.models import User, Note, Tag
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


@app.route('/notes', defaults={'username': None}, methods=['GET', 'POST'])
@app.route('/<username>/notes', methods=['GET', 'POST'])
@login_required
def notes(username):
    if username is None:
        username = current_user.username

    note_id = request.args.get('note_id', None, type=int)
    new_flag = request.args.get('new_flag', False, type=bool)
    edit_flag = request.args.get('edit_flag', False, type=bool)
    filter_tags = request.args.getlist('filter_tags')
    if not filter_tags:
        filter_tags = request.form.getlist('filter_tags')
        if filter_tags:
            return redirect(url_for('notes', username=username, filter_tags=filter_tags))

    user = User.query.filter_by(username=username).first()
    if user is None:
        return redirect(url_for('notes'))

    if not filter_tags:
        notes = user.notes.order_by(Note.update_time.desc()).all()
    else:
        notes = []
        for tag in filter_tags:
            if user.tags.filter_by(name=tag).first() is not None:
                notes_tmp = user.tags.filter_by(name=tag).first().notes.all()
                if notes_tmp is not None:
                    for note in notes_tmp:
                        if note not in notes:
                            notes.append(note)
        notes.sort(key=lambda x: x.update_time, reverse=True)

    form = NoteForm()

    if form.validate_on_submit():
        if request.form['submit'] == 'Create':
            # Creating new note - always for current_user
            new_flag = False
            note = Note(title=form.title.data, body=form.body.data, user_id=current_user.id)
            db.session.add(note)
            note.edit_tags(form.tags.data.split())
            flash('Created new note. Title: {}'.format(note.title))
            return redirect(url_for('notes', username=current_user.username, filter_tags=filter_tags))

        elif request.form['submit'] == 'Accept':
            # Editing existing note
            edit_flag = False
            if note_id is not None:
                note = user.notes.filter_by(id=note_id).first()
                if note is not None:
                    tags = ""
                    for tag in note.tags:
                        tags += tag.name + " "
                    if note.title != form.title.data or note.body != form.body.data or tags != form.tags.data:
                        note.title = form.title.data
                        note.body = form.body.data
                        note.update_time = datetime.utcnow()
                        note.edit_tags(form.tags.data.split())
                        flash('Saved changes to note. Title: {}'.format(note.title))
                    else:
                        flash('There is no change provided')
                else:
                    flash('No data found')
            else:
                flash('No data found')

            return redirect(url_for('notes', username=username, note_id=note_id, filter_tags=filter_tags))

    elif note_id is not None and edit_flag:
        # load data to the edit-form
        note = user.notes.filter_by(id=note_id).first()
        if note is not None:
            form.title.data = note.title
            form.body.data = note.body
            tags = ""
            for tag in note.tags:
                tags += tag.name + " "
            form.tags.data = tags
        else:
            flash('No data found')

    return render_template(
        'notes.html',
        username=username,
        form=form,
        notes=notes,
        note_id=note_id,
        new_flag=new_flag,
        edit_flag=edit_flag,
        filter_tags=filter_tags)


@app.route('/del_note/<note_id>')
@login_required
def del_note(note_id):
    filter_tags = request.args.getlist('filter_tags')

    note = current_user.notes.filter_by(id=note_id).first()
    if note is not None:
        flash('Deleted note: {}'.format(note.title))
        note.edit_tags([])
        db.session.delete(note)
        db.session.commit()
    else:
        flash("No data found")
    return redirect(url_for('notes', username=current_user.username, filter_tags=filter_tags))


@app.route('/tags', defaults={'username': None}, methods=['GET', 'POST'])
@app.route('/<username>/tags', methods=['GET', 'POST'])
@login_required
def tags(username):
    if username is None:
        username = current_user.username

    user = User.query.filter_by(username=username).first()
    if user is None:
        return redirect(url_for('tags'))

    order_by = request.args.get('order_by', None, type=str)
    if order_by != 'name' and order_by != 'timestamp':
        order_by = 'name'
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
            new_tags_form.names.data = None
            flash('Created new tags: {}'.format(list_str))

    elif edit_tag_form.validate_on_submit():
        tag = user.tags.filter_by(id=tag_id).first()
        tag_list = edit_tag_form.name.data.split()
        if tag_list[0] is not None:
            if user.tags.filter_by(name=tag_list[0]).first() is None:
                flash('Changed tag name from {old} to {new}'.format(old=tag.name, new=tag_list[0]))
                tag.name = tag_list[0]
                tag.timestamp = datetime.utcnow()
                db.session.commit()
                tag_id = None
            else:
                flash('There is such tag already')

    if tag_id is not None:
        tag = user.tags.filter_by(id=tag_id).first()
        if tag is not None:
            edit_tag_form.name.data = tag.name

    if order_by == 'name':
        tags = user.tags.order_by(Tag.name)
    else:
        tags = user.tags.order_by(Tag.timestamp.desc())

    return render_template(
        'tags.html',
        username=username,
        tag_id=tag_id, order_by=order_by,
        newTagsForm=new_tags_form, editTagForm=edit_tag_form,
        tags=tags
    )


@app.route('/del_tag/<tag_id>')
@login_required
def del_tag(tag_id):
    tag = current_user.tags.filter_by(id=tag_id).first()
    order_by = request.args.get('order_by', None, type=str)
    if order_by != 'name' and order_by != 'timestamp':
        order_by = 'name'

    if tag is not None:
        flash('Deleted tag: {}'.format(tag.name))
        db.session.delete(tag)
        db.session.commit()
    else:
        flash('No data found')

    return redirect(url_for('tags', order_by=order_by))

