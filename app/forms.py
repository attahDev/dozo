from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, DateField, TimeField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, ValidationError
from app.models import User


class LoginForm(FlaskForm):
    email    = StringField('Email',    validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(3, 64)])
    email    = StringField('Email',    validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm  = PasswordField('Confirm',  validators=[DataRequired(), EqualTo('password')])

    def validate_username(self, f):
        if User.query.filter_by(username=f.data).first():
            raise ValidationError('Username taken.')
    def validate_email(self, f):
        if User.query.filter_by(email=f.data).first():
            raise ValidationError('Email already registered.')


class TodoForm(FlaskForm):
    title    = StringField('Title',    validators=[DataRequired(), Length(max=256)])
    priority = SelectField('Priority', choices=[('low','Low'),('normal','Normal'),('high','High')], default='normal')
    due_date = DateField('Due Date', validators=[Optional()])
    due_time = TimeField('Due Time', validators=[Optional()])


class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(3, 64)])
    email    = StringField('Email',    validators=[DataRequired(), Email()])
    bio      = TextAreaField('Bio',    validators=[Optional(), Length(max=300)])

    def __init__(self, orig_username, orig_email, *a, **kw):
        super().__init__(*a, **kw)
        self._orig_user  = orig_username
        self._orig_email = orig_email

    def validate_username(self, f):
        if f.data != self._orig_user and User.query.filter_by(username=f.data).first():
            raise ValidationError('Username taken.')
    def validate_email(self, f):
        if f.data != self._orig_email and User.query.filter_by(email=f.data).first():
            raise ValidationError('Email taken.')


class ChangePasswordForm(FlaskForm):
    current  = PasswordField('Current Password', validators=[DataRequired()])
    new      = PasswordField('New Password',     validators=[DataRequired(), Length(min=8)])
    confirm  = PasswordField('Confirm',          validators=[DataRequired(), EqualTo('new')])