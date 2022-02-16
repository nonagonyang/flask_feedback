from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired

# This form should accept a username, password, email, first_name, and last_name.
class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    email=StringField("Email",validators=[InputRequired()])
    first_name=StringField("FirstName", validators=[InputRequired()])
    last_name=StringField("LastName",validators=[InputRequired()])

# Show a form that when submitted will login a user. 
# This form should accept a username and a password.
class LoginForm(FlaskForm):
    username=StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])


class FeedbackForm(FlaskForm):
    title=StringField("Title", validators=[InputRequired()])
    content=StringField("Content", validators=[InputRequired()])