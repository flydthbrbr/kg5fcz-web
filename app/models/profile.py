
from app.extensions import db


class UserProfile(db.Model):
    __tablename__ = "user_profiles"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    display_name = db.Column(
        db.String(100),
        nullable=True,
    )

    grid_square = db.Column(
        db.String(8),
        nullable=True,
    )

    timezone = db.Column(
        db.String(64),
        nullable=False,
        default="UTC",
    )

    preferred_units = db.Column(
        db.String(16),
        nullable=False,
        default="imperial",
    )

    user = db.relationship(
        "User",
        back_populates="profile",
    )

    def __repr__(self) -> str:
        return f"<UserProfile user_id={self.user_id}>"
