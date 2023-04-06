from django.conf import settings
from django_silly_auth.exceptions import SillyAuthError
from django_silly_auth.templates.helpers import dsa_template_path

print("=== IMPORT django_silly_auth.config")

SILLY_AUTH_SETTINGS = {
    # General settings
    "SITE_NAME": None,  # str used in templates if provided
    "SITE_URL": None,  # http:// entry url ('index') used in templates if provided
    "USE_DRF": True,  # False for only classic django views
    "FULL_CLASSIC": False,  # False if you use DRF, for Django classic True gets you all out of the box.
    "BASE_TEMPLATE": dsa_template_path("silly_auth/_base.html"),  # if you use the provided templates
    #  DSA dev only, FULL_CLASSIC testing base template:
    # "BASE_TEMPLATE": dsa_template_path("silly_auth/_test/_base.html"),
    "TEMPLATES_TITLE": "D.S. AUTH",  # title if you use the provided templates


    # For development,
    "TEST_TEMPLATES": False,  # for dev only,  opens 2 "_test/" endpoints
    "GET_ALL_USERS": False,  # True for dev tests only, opens the GET 'users/' endpoint
    "PRINT_WARNINGS": True,  # print warnings to terminal

    # emails settings
    "EMAIL_TERMINAL_PRINT": True,  # print emails to terminal
    "EMAIL_VALID_TIME": 600,  # seconds

    # login / logout (DRF views if USE_DRF == True)
    "ALLOW_LOGIN_ENDPOINT": True,  # activate this endpoint
    "LOGIN_REDIRECT": None,  # set an endpoint to redirect to after successfull login
    "ALLOW_LOGOUT_ENDPOINT": True,  # activate this endpoint

    # account creation (DRF views if USE_DRF == True)
    "ALLOW_CREATE_USER_ENDPOINT": True,  # activate this endpoint
    "ALLOW_EMAIL_CONFIRM_ENDPOINT": True,  # activate this 'GET' endpoint (hook for email link)
    "EMAIL_SEND_ACCOUNT_CONFIRM_LINK": True,
    "ACCOUNT_CONFIRMED_REDIRECT": None,
    "EMAIL_CONFIRM_ACCOUNT_TEMPLATE":
        dsa_template_path("silly_auth/emails/confirm_email.txt"),

    # password reset (forgotten password, contains classic views, accepts GET from email link)
    "ALLOW_RESET_PASSWORD_ENDPOINT": True,  # activate this endpoint
    "EMAIL_SEND_PASSWORD_RESET_LINK": True,
    "EMAIL_RESET_PASSWORD_TEMPLATE":  # email template
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

    # FULL_CLASSIC templates, if you use FULL_CLASSIC == True, change this to your own templates
    "USE_CLASSIC_INDEX": True,  # if False, your url route must have the name='classic_index'
    "CLASSIC_INDEX": dsa_template_path("silly_auth/classic/index.html"),
    "USE_CLASSIC_ACCOUNT": True,  # if False, your url route must have the name='classic_account'
    "CLASSIC_ACCOUNT": dsa_template_path("silly_auth/classic/account.html"),
    "CLASSIC_SIGNUP": dsa_template_path("silly_auth/classic/signup.html"),
    "CLASSIC_LOGIN": dsa_template_path("silly_auth/classic/login.html"),
    "CLASSIC_CHANGE_EMAIL": dsa_template_path("silly_auth/classic/change_email.html"),
    "CLASSIC_CHANGE_USERNAME": dsa_template_path("silly_auth/classic/change_username.html"),
    "CLASSIC_REQUEST_PASSWORD_RESET": dsa_template_path("silly_auth/classic/request_password_reset.html"),
    "CLASSIC_RESET_PASSWORD": dsa_template_path("silly_auth/classic/reset_password.html"),
    "CLASSIC_REQUEST_RESEND_ACCOUNT_CONFIRMATION_EMAIL": "silly_auth/classic/request_resend_account_confirmation_email.html",


}

# Overwrite SILLY_AUTH_SETTINGS with datas from  settings.SILLY_AUTH
try:
    for key in settings.SILLY_AUTH:
        if key not in SILLY_AUTH_SETTINGS:
            raise SillyAuthError(f"Unexpected key in settings.SILLY_AUTH: '{key}'")
        SILLY_AUTH_SETTINGS[key] = settings.SILLY_AUTH[key]
except AttributeError:
    pass
