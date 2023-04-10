
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.db import transaction

from django_silly_auth.config import SILLY_AUTH_SETTINGS as conf


if conf["VERBOSE"]:
    print("=== DSA IMPORT django_silly_auth.views.classics")

User = get_user_model()


@transaction.atomic
def silly_confirm_email(request, token):
    user = User.verify_jwt_token(token)
    if user is None:
        msg = _("Invalid or expired token"),
        tag = "danger"
    if user is not None and user.is_active:
        if not user.is_confirmed:
            user.is_confirmed = True
            user.new_email = None
            msg = _("Your account have been confirmed")
            tag = "success"
            user.save()
        elif user.new_email:
            user.email = user.new_email
            user.new_email = None
            msg = _("Your new email have been confirmed")
            tag = "success"
            user.save()
        else:
            msg = _("Your account is already confirmed")
            tag = "warning"

    context = {
        "base_template": conf["BASE_TEMPLATE"],
        "message": msg,
        "tag": tag,
        "link": conf["SILLY_LINK_TO_SPA"],
        "site_name": conf["SITE_NAME"],
    }
    return render(request, 'silly_auth/silly/silly_confirm_email.html', context)


def silly_password_reset_done(request):
    msg = _("Your password has been reset")
    context = {
        "base_template": conf["BASE_TEMPLATE"],
        "message": msg,
        "tag": "success",
        "link": conf["SILLY_LINK_TO_SPA"],
        "site_name": conf["SITE_NAME"],
    }
    return render(request, 'silly_auth/silly/silly_confirm_email.html', context)