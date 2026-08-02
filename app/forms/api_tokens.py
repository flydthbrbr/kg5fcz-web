from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Length, Optional


class CreateApiTokenForm(FlaskForm):
    name = StringField(
        "Token name",
        validators=[
            Optional(),
            Length(
                max=100,
                message="Token name must be 100 characters or fewer.",
            ),
        ],
    )

    submit = SubmitField("Create token")


class RevokeApiTokenForm(FlaskForm):
    submit = SubmitField("Revoke")
