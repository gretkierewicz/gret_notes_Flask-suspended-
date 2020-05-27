from app import db, login
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    notes = db.relationship('Note', backref='owner', lazy='dynamic')
    tags = db.relationship('Tag', backref='owner', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


note_tag = db.Table('note_tag',
                    db.Column('note_id', db.Integer, db.ForeignKey('note.id')),
                    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
                    )


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), index=True)
    body = db.Column(db.String(1024))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))   # backref in User: owner
    tags = db.relationship('Tag', secondary=note_tag, lazy='dynamic')

    def __repr__(self):
        return '<Note {}>'.format(self.title)

    def set_tag(self, tag):
        if not self.is_tagged(tag):
            self.tags.append(tag)

    def del_tag(self, tag):
        if self.is_tagged(tag):
            self.tags.remove(tag)

    def is_tagged(self, tag):
        return self.tags.filter(note_tag.c.tag_id == tag.id).count() > 0

    def edit_tags_with_list(self, tags_list):
        """
        Edit tags providing list of tags in string format.
        :param tags_list: List of tags in string format
        """
        for tag in self.tags:  # look for tags to remove
            if tag.name not in tags_list:
                self.tags.remove(tag)
        for tag_name in tags_list:  # look for tags to add
            tag = self.owner.tags.filter_by(name=tag_name).first()
            if tag is None:
                tag = Tag(name=tag_name, user_id=self.owner.id)
                self.tags.append(tag)
            else:
                if not self.is_tagged(tag):
                    self.tags.append(tag)
        db.session.commit()


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))   # backref in User: owner
    notes = db.relationship('Note', secondary=note_tag, lazy='dynamic')

    def __repr__(self):
        return '<Tag {}>'.format(self.name)
