from email.utils import parseaddr

from email_validator import validate_email, EmailNotValidError
from flask import request, current_app, render_template
from flask_imp.auth import generate_private_key

from app.services import send_zepto_email
from app.models.accounts import Accounts
from app.utilities.datetime_delta import DatetimeDelta
from app.config import zepto_service_settings
from .. import bp


@bp.post("/login")
def login():
    jsond = request.json

    name, email_address = parseaddr(jsond.get("email_address"))

    if not email_address:
        return {"status": "error", "message": "Email address is not valid."}

    try:
        validate_email(email_address)
    except EmailNotValidError:
        return {"status": "error", "message": "Email address is not valid."}

    account = Accounts.get_account(email_address)

    url = f"{current_app.config['SET_HOST_URL']}/auth"

    if not account:
        pk = generate_private_key(f"{DatetimeDelta().datetime}{email_address}")
        new_account = Accounts.um_create(
            {
                "email_address": email_address,
                "settings": {"theme": "dark", "units": "kgs"},
                "auth_code": pk,
                "auth_code_expiry": DatetimeDelta().days(30).datetime,
            },
            return_record=True,
        )

        send_zepto_email(
            zepto_service_settings,
            recipients=[email_address],
            subject="Welcome to idosets.app!",
            body=render_template(
                "welcome-email.html",
                url=url,
                account_id=new_account.account_id,
                auth=pk,
            ),
        )

        return {
            "status": "success",
            "message": "New account created, login email sent.",
        }

    pk = generate_private_key(f"{DatetimeDelta().datetime}{email_address}")
    account.update_auth_code(pk, DatetimeDelta().days(30).datetime)

    send_zepto_email(
        zepto_service_settings,
        recipients=[email_address],
        subject="Here's your login link!",
        body=render_template(
            "login-email.html",
            url=url,
            account_id=account.account_id,
            auth=pk,
        ),
    )

    return {
        "status": "success",
        "message": "Login email sent.",
    }
