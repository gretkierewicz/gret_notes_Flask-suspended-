from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class NoteForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    body = TextAreaField('Body', validators=[Length(max=1024)])
    tags = TextAreaField('Tags', validators=[Length(max=1024)])
    submit = SubmitField()


class NewTagForm(FlaskForm):
    names = StringField('Names', validators=[DataRequired()])
    submit = SubmitField('Create')


class EditTagForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Accept')
