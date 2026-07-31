from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp


class RegistrationForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email(),
            Length(max=255),
        ],
    )

    callsign = StringField(
        "Callsign",
        validators=[
            DataRequired(),
            Length(min=3, max=20),
            Regexp(
                r"^[A-Za-z0-9/]+$",
                message="Callsign may contain only letters, numbers, and /.",
            ),
        ],
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(
                min=12,
                message="Password must be at least 12 characters.",
            ),
        ],
    )

    password_confirm = PasswordField(
        "Confirm password",
        validators=[
            DataRequired(),
            EqualTo(
                "password",
                message="Passwords must match.",
            ),
        ],
    )

    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    identity = StringField(
        "Email or callsign",
        validators=[
            DataRequired(),
            Length(max=255),
        ],
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
        ],
    )

    remember_me = BooleanField("Remember me")

    submit = SubmitField("Sign in")
