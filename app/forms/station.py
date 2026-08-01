from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import Length, Optional, Regexp


class StationForm(FlaskForm):
    station_name = StringField(
        "Station name",
        validators=[Optional(), Length(max=100)],
    )

    grid_square = StringField(
        "Maidenhead grid square",
        validators=[
            Optional(),
            Regexp(
                r"^[A-Ra-r]{2}[0-9]{2}([A-Xa-x]{2})?([0-9]{2})?$",
                message="Enter a valid 4-, 6-, or 8-character grid square.",
            ),
        ],
    )

    primary_rig = StringField(
        "Primary rig",
        validators=[Optional(), Length(max=100)],
    )

    primary_antenna = StringField(
        "Primary antenna",
        validators=[Optional(), Length(max=150)],
    )

    license_class = SelectField(
        "License class",
        choices=[
            ("", "Not specified"),
            ("Technician", "Technician"),
            ("General", "General"),
            ("Amateur Extra", "Amateur Extra"),
            ("Advanced", "Advanced"),
            ("Novice", "Novice"),
            ("Other", "Other"),
        ],
        validators=[Optional()],
    )

    dxcc_entity = StringField(
        "DXCC entity",
        validators=[Optional(), Length(max=100)],
    )

    submit = SubmitField("Save station")
