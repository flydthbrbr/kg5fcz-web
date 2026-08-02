from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required

from app.extensions import db
from app.forms import (
    CreateApiTokenForm,
    RevokeApiTokenForm,
)
from app.models import ApiToken
from app.services.api_tokens import (
    generate_api_token,
    revoke_api_token,
)


account_api_tokens = Blueprint(
    "account_api_tokens",
    __name__,
)


@account_api_tokens.route(
    "/account/api-tokens",
    methods=["GET", "POST"],
)
@login_required
def manage_api_tokens():
    """Create and list API tokens for the current user."""

    create_form = CreateApiTokenForm()
    revoke_form = RevokeApiTokenForm()

    if create_form.validate_on_submit():
        record, raw_token = generate_api_token(
            current_user,
            name=create_form.name.data or "OpenHamClock",
            scope="clock:read",
        )

        db.session.commit()

        session["new_api_token"] = {
            "id": record.id,
            "name": record.name,
            "token": raw_token,
        }

        flash(
            "API token created. Copy it now; it will not be shown again.",
            "success",
        )

        return redirect(
            url_for(
                "account_api_tokens.manage_api_tokens"
            )
        )

    tokens = db.session.scalars(
        db.select(ApiToken)
        .where(ApiToken.user_id == current_user.id)
        .order_by(ApiToken.created_at.desc())
    ).all()

    new_token = session.pop("new_api_token", None)

    return render_template(
        "auth/api_tokens.html",
        create_form=create_form,
        revoke_form=revoke_form,
        tokens=tokens,
        new_token=new_token,
    )


@account_api_tokens.post(
    "/account/api-tokens/<int:token_id>/revoke"
)
@login_required
def revoke_token(token_id: int):
    """Revoke one API token owned by the current user."""

    form = RevokeApiTokenForm()

    if not form.validate_on_submit():
        flash(
            "The token could not be revoked.",
            "error",
        )
        return redirect(
            url_for(
                "account_api_tokens.manage_api_tokens"
            )
        )

    record = db.session.scalar(
        db.select(ApiToken).where(
            ApiToken.id == token_id,
            ApiToken.user_id == current_user.id,
        )
    )

    if record is None:
        flash(
            "API token not found.",
            "warning",
        )
        return redirect(
            url_for(
                "account_api_tokens.manage_api_tokens"
            )
        )

    revoke_api_token(record)
    db.session.commit()

    flash(
        f"API token '{record.name}' was revoked.",
        "success",
    )

    return redirect(
        url_for(
            "account_api_tokens.manage_api_tokens"
        )
    )
