from app.extensions import db
from app.models import ClockSettings, User


def get_or_create_clock_settings(
    user: User,
) -> ClockSettings:
    """
    Return the user's clock settings, creating defaults when absent.

    The new object is added to the current database session, but this
    function does not commit the transaction.
    """

    if user.clock_settings is not None:
        return user.clock_settings

    settings = ClockSettings(
        user=user,
        theme="dark",
        units="imperial",
        map_projection="mercator",
        show_satellites=True,
        show_dx_cluster=True,
        show_weather=True,
        show_moon=True,
        show_grayline=True,
        default_zoom=2,
    )

    db.session.add(settings)

    return settings

