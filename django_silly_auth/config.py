from django.conf import settings
from django_silly_auth.exceptions import SillyAuthError
from django_silly_auth.templates.helpers import dsa_template_path

print("=== IMPORT django_silly_auth.config")

SILLY_AUTH_SETTINGS = {
    # General settings
    "SITE_NAME": None,  # str used in templates if provided
    "SITE_URL": None,  # http:// entry url ('index') used in templates if provided
    "USE_DRF": True,  # False for only classic django views
    "USE_ALL_TEMPLATES": False,  # False recommended if you use DRF, otherwise True is good to go fast.
    "BASE_TEMPLATE": dsa_template_path("silly_auth/_base.html"),  # if you use the provided templates

    "GET_ALL_USERS": False,  # True for dev tests only, opens the endpoint
    "PRINT_WARNINGS": True,  # print warnings to terminal

    # emails settings
    "EMAIL_TERMINAL_PRINT": True,  # print emails to terminal
    "EMAIL_VALID_TIME": 600,  # seconds

    # login / logout (DRF views)
    "ALLOW_LOGIN_ENDPOINT": True,  # activate this endpoint
    "LOGIN_REDIRECT": None,  # set an endpoint to redirect to after successfull login
    "ALLOW_LOGOUT_ENDPOINT": True,  # activate this endpoint

    # account creation (DRF views)
    "ALLOW_CREATE_USER_ENDPOINT": True,  # activate this endpoint
    "ALLOW_EMAIL_CONFIRM_ENDPOINT": True,  # activate this 'GET' endpoint (hook for email link)
    "EMAIL_SEND_ACCOUNT_CONFIRM_LINK": True,
    "ACCOUNT_CONFIRMED_REDIRECT": None,
    "EMAIL_CONFIRM_ACCOUNT_TEMPLATE":
        dsa_template_path("silly_auth/emails/confirm_email.txt"),

    # password reset (forgotten password, contains classic views, accepts GET from email link)
    "ALLOW_RESET_PASSWORD_ENDPOINT": True,  # activate this endpoint
    "EMAIL_SEND_PASSWORD_RESET_LINK": True,
    "EMAIL_RESET_PASSWORD_TEMPLATE":
        dsa_template_path("silly_auth/emails/request_password_reset.txt"),
    #   default frontend are classic django views, you can change it to
    #   your own views and/or templates
    "RESET_PASSWORD_ENDPOINT": "auth/password/reset/",
    "RESET_PASSWORD_TEMPLATE": dsa_template_path("silly_auth/reset_password.html"),
    "RESET_PASSWORD_DONE_TEMPLATE": dsa_template_path("silly_auth/reset_password_done.html"),

    # password change (DRF view)
    "ALLOW_CHANGE_PASSWORD_ENDPOINT": True,  # activate this endpoint

    # email change (DRF view)
    "ALLOW_CHANGE_EMAIL_ENDPOINT": True,  # activate this endpoint
    "EMAIL_SEND_NEW_EMAIL_CONFIRM_LINK": True,

    "ALLOW_CONFIRM_NEW_EMAIL_HOOK_ENDPOINT": True,  # activate this 'GET' endpoint (hook for email link)
    # if Flase, change this:
    "CONFIRM_NEW_EMAIL_HOOK_ENDPOINT": "confirm_new_email/<token>/",  # default is a classic view
    "NEW_EMAIL_CONFIRM_TEMPLATE": dsa_template_path("silly_auth/new_email_confirm.html"),  # if new email hook activated
    "NEW_EMAIL_CONFIRMED_DONE_TEMPLATE": dsa_template_path("silly_auth/new_email_confirmed_done.html"),  # if new email hook activated

    # for DSA dev,
    "TEST_TEMPLATES": False,  # for dev,  opens 2 "_test/" endpoints

}

try:
    for key in settings.SILLY_AUTH:
        if key not in SILLY_AUTH_SETTINGS:
            raise SillyAuthError(f"Unexpected key in settings.SILLY_AUTH: '{key}'")
        SILLY_AUTH_SETTINGS[key] = settings.SILLY_AUTH[key]
except AttributeError:
    pass
