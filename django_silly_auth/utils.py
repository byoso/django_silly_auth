from functools import wraps
from threading import Thread
import time

from django.conf import settings
from django.shortcuts import reverse
from django.core.mail import send_mail
from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _

from smtplib import SMTPServerDisconnected

from django_silly_auth.config import SILLY_AUTH_SETTINGS as conf


if conf["VERBOSE"]:
    print("=== DSA IMPORT django_silly_auth.utils")


def dsa_thread(func):
    """decorator that simply runs the function in parallel thread"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        send = Thread(target=func, args=args, kwargs=kwargs, daemon=True)
        send.start()
    return wrapper


@dsa_thread
def delete_unconfirmed(user, *args, **kwargs):
    if conf["VERBOSE"]:
        print(
            f"=== {user} created, waiting for confirmation..."
            f"{conf['DELETE_UNCONFIRMED_TIME']} hours")
    if conf["DELETE_UNCONFIRMED_TIME"] > 0.0:
        time.sleep(conf["DELETE_UNCONFIRMED_TIME"] * 3600.0)
        if not user.is_confirmed:
            if conf["VERBOSE"]:
                print(f"=== {user} deleted")
            user.delete()


def dsa_send_mail(*args, **kwargs):
    send = Thread(target=send_mail, args=args, kwargs=kwargs, daemon=True)
    send.start()


def send_password_reset_email(request, user):
    token = user.get_jwt_token(expires_in=conf["EMAIL_VALID_TIME"])
    domain = request.build_absolute_uri('/')[:-1]
    if conf["CONFIRMATION_METHOD"] == 'GET':
        link = domain + reverse('classic_reset_password', args=[token])
    if conf["CONFIRMATION_METHOD"] == 'POST':
        link = conf['SPA_EMAIL_LOGIN_LINK'] + f"{token}"
    context = {
        'user': user,
        'link': link,
        'site_name': conf["SITE_NAME"]
    }

    msg_text = get_template(conf["EMAIL_RESET_PASSWORD_TEMPLATE"])
    if conf["EMAIL_TERMINAL_PRINT"]:
        print("from ", settings.EMAIL_HOST_USER)
        print(msg_text.render(context))

    dsa_send_mail(
        'Password reset request',
        msg_text.render(context),
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )


def send_confirm_email(request, user, new_email=False):
    token = user.get_jwt_token(expires_in=conf["EMAIL_VALID_TIME"])
    domain = request.build_absolute_uri('/')[:-1]
    # if new_email:
    if conf["USE_SILLY"]:
        link = domain + reverse('dsa_confirm_email', args=[token])
    elif conf["CONFIRMATION_METHOD"] == 'GET':
        link = domain + reverse('classic_confirm_email', args=[token])
    if conf["CONFIRMATION_METHOD"] == 'POST':
        link = conf['SPA_EMAIL_LOGIN_LINK'] + f"{token}"
    context = {
        'user': user,
        'link': link,
        'site_name': conf["SITE_NAME"],
    }

    msg_text = get_template(conf["EMAIL_CONFIRM_ACCOUNT_TEMPLATE"])

    if conf["EMAIL_TERMINAL_PRINT"]:
        print("from ", settings.EMAIL_HOST_USER)
        print(msg_text.render(context))

    if new_email:
        email = user.new_email
    else:
        email = user.email

    dsa_send_mail(
        'Confirm your new email',
        msg_text.render(context),
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )
