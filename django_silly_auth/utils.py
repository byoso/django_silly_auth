from django.conf import settings
from django.shortcuts import reverse
from django.core.mail import send_mail
from django.template.loader import get_template
from django.contrib import messages

from smtplib import SMTPServerDisconnected

from django_silly_auth.config import SILLY_AUTH_SETTINGS as conf
from django_silly_auth.views.views import reset_password

# email address to send emails from
EMAIL_HOST_USER = settings.EMAIL_HOST_USER
validity_time = conf["EMAIL_VALID_TIME"]
email_confirm_account_template = conf["EMAIL_CONFIRM_ACCOUNT_TEMPLATE"]
email_reset_password_template = conf["EMAIL_RESET_PASSWORD_TEMPLATE"]
site_name = conf["SITE_NAME"]
terminal_print = conf["EMAIL_TERMINAL_PRINT"]
# print_warnings = conf["PRINT_WARNINGS"]
reset_password_endpoint = conf["RESET_PASSWORD_ENDPOINT"]


def send_password_reset_email(request, user):
    token = user.get_jwt_token(expires_in=validity_time)
    domain = request.build_absolute_uri('/')[:-1]
    link = domain + reverse(reset_password, args=[token])
    context = {
        'user': user,
        'link': link,
        'site_name': site_name
    }

    msg_text = get_template(email_reset_password_template)
    if terminal_print:
        print("from ", EMAIL_HOST_USER)
        print(msg_text.render(context))

    send_mail(
        'Password reset request',
        msg_text.render(context),
        EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )


def send_confirm_email(request, user, new_email=False):
    token = user.get_jwt_token(expires_in=validity_time)
    domain = request.build_absolute_uri('/')[:-1]
    if new_email:
        link = domain + reverse('confirm_new_email', args=[token])
    else:
        link = domain + reverse('confirm_email', args=[token])
    context = {
        'user': user,
        'link': link,
        'site_name': site_name,
    }

    msg_text = get_template(email_confirm_account_template)

    if terminal_print:
        print("from ", EMAIL_HOST_USER)
        print(msg_text.render(context))

    if new_email:
        email = user.new_email
    else:
        email = user.email

    send_mail(
        'Confirm your new email',
        msg_text.render(context),
        EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )


class Color:
    """
    Color class for terminal output
    """
    end = "\x1b[0m"
    info = "\x1b[0;30;36m"
    success = "\x1b[0;30;32m"
    warning = "\x1b[0;30;33m"
    danger = "\x1b[0;30;31m"


def warning(msg):
    if conf["PRINT_WARNINGS"] is True:
        print(Color.warning + msg + Color.end)


def danger(msg):
    if conf["PRINT_WARNINGS"] is True:
        print(Color.danger + msg + Color.end)
