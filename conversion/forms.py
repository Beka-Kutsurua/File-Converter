from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from conversion.models import User

class RegisterForm(FlaskForm):

    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError('Username already exists. Please try a different username')
        
    def validate_email_adress(self, email_adress_to_check):
        email_adress = User.query.filter_by(email_adress=email_adress_to_check.data).first()
        if email_adress:
            raise ValidationError('Email already exists. Please try a different email adress')

    username = StringField(label='User Name:', validators=[Length(min=2, max=30), DataRequired()])
    email_adress = StringField(label='Email Adress:', validators=[Email(), DataRequired()])
    password1 = PasswordField(label='Password', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label='Confirm Password', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Create Account')

class LoginForm(FlaskForm):
    username = StringField(label="User Name", validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label='Sign In')

class DeleteForm(FlaskForm):
    submit = SubmitField(label='Delete')
