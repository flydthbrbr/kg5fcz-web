from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, SelectField, SubmitField
from wtforms.validators import NumberRange


class ClockSettingsForm(FlaskForm):
    theme = SelectField(
        "Theme",
        choices=[
            ("dark", "Dark"),
            ("light", "Light"),
        ],
    )

    units = SelectField(
        "Units",
        choices=[
            ("imperial", "Imperial"),
            ("metric", "Metric"),
        ],
    )

    map_projection = SelectField(
        "Map projection",
        choices=[
            ("mercator", "Mercator"),
            ("azimuthal", "Azimuthal"),
        ],
    )

    show_satellites = BooleanField("Show satellites")
    show_dx_cluster = BooleanField("Show DX cluster")
    show_weather = BooleanField("Show weather")
    show_moon = BooleanField("Show moon")
    show_grayline = BooleanField("Show grayline")

    default_zoom = IntegerField(
        "Default zoom",
        validators=[
            NumberRange(
                min=1,
                max=10,
                message="Zoom must be between 1 and 10.",
            ),
        ],
    )

    submit = SubmitField("Save clock settings")
