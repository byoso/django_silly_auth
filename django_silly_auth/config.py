from django.conf import settings


class SillyAuthError(Exception):
    pass


SILLY_AUTH_SETTINGS = {
    # Quick settings
    "AUTO_SET": 'TEST',  # 'CLASSIC', 'SPA', 'SILLY or 'TEST'
    "DSA_PREFIX": 'auth/',

    # Secondary settings
    "SITE_NAME": None,  # str used in templates if provided
    "DELETE_UNCONFIRMED_TIME": 24.0,  # hours after what an unconfirmed account is deleted, O to set off

    # Classic settings
    "USE_CLASSIC": True,
        # redirections
    "USE_CLASSIC_INDEX": True,  # if False, your index route must have the name='classic_index'
    "USE_CLASSIC_ACCOUNT": True,  # if False, your account route must have the name='classic_account'
        # templates settings
    "TEMPLATES_TITLE": "D.S. AUTH",  # title if you use the provided templates
    "BASE_TEMPLATE": "silly_auth/_base.html",  # if you use the provided templates
        # templates paths
    "CLASSIC_INDEX": "silly_auth/classic/index.html",
    "CLASSIC_ACCOUNT": "silly_auth/classic/account.html",
    "CLASSIC_SIGNUP": "silly_auth/classic/signup.html",
    "CLASSIC_LOGIN": "silly_auth/classic/login.html",
    "CLASSIC_CHANGE_EMAIL": "silly_auth/classic/change_email.html",
    "CLASSIC_CHANGE_USERNAME": "silly_auth/classic/change_username.html",
    "CLASSIC_REQUEST_PASSWORD_RESET": "silly_auth/classic/request_password_reset.html",
    "CLASSIC_RESET_PASSWORD": "silly_auth/classic/reset_password.html",
    "CLASSIC_REQUEST_RESEND_ACCOUNT_CONFIRMATION_EMAIL": "silly_auth/classic/request_resend_account_confirmation_email.html",

    # DRF settings
    "USE_DRF": False,  # False for only classic django views
    "CONFIRMATION_METHOD": 'GET',  # 'GET' or 'POST'
    "ALLOW_CREATE_USER_ENDPOINT": True,  # activate this endpoint

    # pure SPA only:
    "SPA_EMAIL_LOGIN_LINK": "http://your spa adress/",  # + <jwt_token>",


    # Silly settings
    "USE_SILLY": False,
    "SILLY_LINK_TO_SPA": None,  # link used in templates to get back to your SPA

    # emails settings
    "EMAIL_TERMINAL_PRINT": True,  # print emails to terminal
    "EMAIL_VALID_TIME": 1200,  # seconds
    "EMAIL_CONFIRM_ACCOUNT_TEMPLATE":
        "silly_auth/emails/confirm_email.txt",
    "EMAIL_RESET_PASSWORD_TEMPLATE":  # email template
        "silly_auth/emails/request_password_reset.txt",

    # For development,
    "TEST_TEMPLATES": False,  # for dev only,  opens 2 "_test/" endpoint
    "VERBOSE": False,  # prints to terminal : imports
}


# Overwrite SILLY_AUTH_SETTINGS with datas from settings.SILLY_AUTH

try:
    settings.SILLY_AUTH
    is_set = True
except AttributeError:
    is_set = False

if is_set and "AUTO_SET" in settings.SILLY_AUTH:
    auto_set = settings.SILLY_AUTH['AUTO_SET']
    if auto_set not in ['CLASSIC', 'SPA', 'SILLY', 'TEST']:
        raise SillyAuthError(
            "AUTO_SET must be 'CLASSIC', 'SPA', 'SILLY or 'TEST'")
else:
    auto_set = SILLY_AUTH_SETTINGS["AUTO_SET"]

match auto_set:
    case "CLASSIC":
        SILLY_AUTH_SETTINGS["USE_DRF"] = False
        SILLY_AUTH_SETTINGS["USE_CLASSIC"] = True
        SILLY_AUTH_SETTINGS["CONFIRMATION_METHOD"] = 'GET'

    case "SPA":
        SILLY_AUTH_SETTINGS["USE_DRF"] = True
        SILLY_AUTH_SETTINGS["USE_CLASSIC"] = False
        SILLY_AUTH_SETTINGS["CONFIRMATION_METHOD"] = 'POST'

    case "SILLY":
        SILLY_AUTH_SETTINGS["USE_DRF"] = True
        SILLY_AUTH_SETTINGS["USE_CLASSIC"] = False
        SILLY_AUTH_SETTINGS["CONFIRMATION_METHOD"] = 'GET'
        SILLY_AUTH_SETTINGS["USE_SILLY"] = True

    case "TEST":
        SILLY_AUTH_SETTINGS["USE_DRF"] = False
        SILLY_AUTH_SETTINGS["USE_CLASSIC"] = True
        SILLY_AUTH_SETTINGS["CONFIRMATION_METHOD"] = 'GET'
        SILLY_AUTH_SETTINGS["BASE_TEMPLATE"] = "silly_auth/_test/_base.html"
        SILLY_AUTH_SETTINGS["TEST_TEMPLATES"] = True
        SILLY_AUTH_SETTINGS["VERBOSE"] = True

if is_set:
    for key in settings.SILLY_AUTH:
        if key not in SILLY_AUTH_SETTINGS:
            raise SillyAuthError(f"Unexpected key in settings.SILLY_AUTH: '{key}'")
        SILLY_AUTH_SETTINGS[key] = settings.SILLY_AUTH[key]


if SILLY_AUTH_SETTINGS["CONFIRMATION_METHOD"] == 'POST' and "SPA_EMAIL_LOGIN_LINK" not in settings.SILLY_AUTH:
    raise SillyAuthError("Confirmation method is 'POST', you must define a SPA_EMAIL_LOGIN_LINK")

try:
    float(SILLY_AUTH_SETTINGS["DELETE_UNCONFIRMED_TIME"])
    assert SILLY_AUTH_SETTINGS["DELETE_UNCONFIRMED_TIME"] >= 0
except (ValueError, AssertionError):
    raise SillyAuthError("DELETE_UNCONFIRMED_TIME must be a positive float, or 0 to set off")


if SILLY_AUTH_SETTINGS["VERBOSE"]:
    print("=== DSA IMPORT django_silly_auth.config")
