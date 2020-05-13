from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Regexp, Length, ValidationError
from app.models import User

class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[
		DataRequired(), 
		Regexp(
			r'[A-Za-z0-9@#$%^&+=]{6,}',
			message='Password need to contain 6 characters including big and small letter, digit and special char'
		)
	])
	confirm_password = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Register')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user is not None:
			raise ValidationError('Please use a different name.')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is not None:
			raise ValidationError('Please use a different email.')

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
