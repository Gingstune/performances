from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange, Length

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    passw = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    passw = PasswordField('Password', validators=[DataRequired()])
    first_name = StringField('First name', validators=[DataRequired()])
    second_name = StringField('Second name', validators=[DataRequired()])
    birthday = StringField('Birthday', validators=[DataRequired()])
    info = StringField('About you')
    submit = SubmitField('Register')
    
class InfoForm(FlaskForm):
    info = StringField('Change info')
    submit = SubmitField('Save')

class RateForm(FlaskForm):
    review = StringField('Review')
    value = SelectField(u'Rate', choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')])
    submit = SubmitField('Send')    
