from urllib.parse import urljoin, urlparse

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,
)
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.forms import LoginForm, ProfileForm, RegistrationForm
from app.models import User, UserProfile


auth = Blueprint("auth", __name__)


def is_safe_redirect_target(target: str | None) -> bool:
    """Return True only when the redirect remains on this website."""

    if not target:
        return False

    host_url = urlparse(request.host_url)
    redirect_url = urlparse(urljoin(request.host_url, target))

    return (
        redirect_url.scheme in {"http", "https"}
        and host_url.netloc == redirect_url.netloc
    )


@auth.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user account."""

    if current_user.is_authenticated:
        return redirect(url_for("auth.account"))

    form = RegistrationForm()

    if form.validate_on_submit():
        normalized_email = form.email.data.strip().lower()
        normalized_callsign = form.callsign.data.strip().upper()

        existing_email = db.session.scalar(
            db.select(User).where(
                func.lower(User.email) == normalized_email
            )
        )

        if existing_email is not None:
            form.email.errors.append(
                "An account already uses that email address."
            )

        existing_callsign = db.session.scalar(
            db.select(User).where(
                func.upper(User.callsign) == normalized_callsign
            )
        )

        if existing_callsign is not None:
            form.callsign.errors.append(
                "An account already uses that callsign."
            )

        if not form.email.errors and not form.callsign.errors:
            user = User(
                email=normalized_email,
                callsign=normalized_callsign,
            )
            user.set_password(form.password.data)

            db.session.add(user)

            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                flash(
                    "That email address or callsign is already registered.",
                    "error",
                )
            else:
                flash(
                    "Registration successful. You can now sign in.",
                    "success",
                )
                return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth.route("/login", methods=["GET", "POST"])
def login():
    """Authenticate an existing user."""

    if current_user.is_authenticated:
        return redirect(url_for("auth.account"))

    form = LoginForm()

    if form.validate_on_submit():
        identity = form.identity.data.strip()

        user = db.session.scalar(
            db.select(User).where(
                or_(
                    func.lower(User.email) == identity.lower(),
                    func.upper(User.callsign) == identity.upper(),
                )
            )
        )

        if user is None or not user.check_password(form.password.data):
            flash("Invalid email, callsign, or password.", "error")
            return render_template("auth/login.html", form=form)

        if not user.is_active:
            flash("This account is disabled.", "error")
            return render_template("auth/login.html", form=form)

        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get("next")

        if is_safe_redirect_target(next_page):
            return redirect(next_page)

        return redirect(url_for("auth.account"))

    return render_template("auth/login.html", form=form)


@auth.post("/logout")
@login_required
def logout():
    """End the authenticated user's session."""

    logout_user()
    flash("You have been signed out.", "success")
    return redirect(url_for("main.index"))


@auth.get("/account")
@login_required
def account():
    """Display the authenticated user's account."""

    return render_template("auth/account.html")


@auth.get("/auth/check")
def auth_check():
    """Return the current authentication state."""

    if not current_user.is_authenticated:
        return {
            "authenticated": False,
        }, 401

    return {
        "authenticated": True,
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "callsign": current_user.callsign,
        },
    }, 200

@auth.route("/account/profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    """Create or update the authenticated user's profile."""

    profile = current_user.profile

    if profile is None:
        profile = UserProfile(user=current_user)

    form = ProfileForm(obj=profile)

    if form.validate_on_submit():
        profile.display_name = (
            form.display_name.data.strip()
            if form.display_name.data
            else None
        )

        profile.grid_square = (
            form.grid_square.data.strip().upper()
            if form.grid_square.data
            else None
        )

        profile.timezone = form.timezone.data
        profile.preferred_units = form.preferred_units.data

        db.session.add(profile)
        db.session.commit()

        flash("Your profile has been updated.", "success")
        return redirect(url_for("auth.edit_profile"))

    return render_template(
        "auth/profile.html",
        form=form,
        profile=profile,
    )
