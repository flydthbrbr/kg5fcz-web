from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import Length, Optional, Regexp


class ProfileForm(FlaskForm):
    display_name = StringField(
        "Display name",
        validators=[
            Optional(),
            Length(max=100),
        ],
    )

    grid_square = StringField(
        "Maidenhead grid square",
        validators=[
            Optional(),
            Regexp(
                r"^[A-Ra-r]{2}[0-9]{2}"
                r"([A-Xa-x]{2})?"
                r"([0-9]{2})?$",
                message=(
                    "Enter a valid 4-, 6-, or 8-character "
                    "Maidenhead grid square."
                ),
            ),
        ],
    )

    timezone = SelectField(
        "Time zone",
        choices=[
            ("UTC", "UTC"),
            ("America/Chicago", "Central Time"),
            ("America/New_York", "Eastern Time"),
            ("America/Denver", "Mountain Time"),
            ("America/Los_Angeles", "Pacific Time"),
            ("America/Anchorage", "Alaska Time"),
            ("Pacific/Honolulu", "Hawaii Time"),
        ],
    )

    preferred_units = SelectField(
        "Preferred units",
        choices=[
            ("imperial", "Imperial"),
            ("metric", "Metric"),
        ],
    )

    submit = SubmitField("Save profile")
