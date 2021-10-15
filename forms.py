from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email
from wtforms.widgets import TextArea


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(message="Username must be entered")])
    password = PasswordField("Password", validators=[InputRequired(message="Password must be entered")])
    email = StringField("Email", validators=[InputRequired(), Email(message="Email must be entered")])
    first_name = StringField("First Name", validators=[InputRequired(message="First name must be entered")])
    last_name = StringField("Last Name", validators=[InputRequired(message="Last name must be entered")])

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(message="Please enter username")])
    password = PasswordField("Password", validators=[InputRequired(message="Please enter password")])

class FeedbackForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired(message="Please enter title")])
    content = StringField("Content", validators=[InputRequired(message="Please enter something")], widget=TextArea())