# Django Silly Auth

## DRF only

Currently only works with Django Rest Framework, not with classic Django.

## installation

### 01 Install the package

```sh
pip install django-silly-auth
```

### 02 Add the mixin to your user model

Note that you need to have a custom user model created somewhere.

**users/models.py** (or wherever is your user model)
```python
from dango_silly_auth.mixins import SillyAuthUserMixin

class User(SillyAuthUserMixin):
    pass

```

**Just to let you know, you don't actually need to use this except 'confirmed' :**

The mixin adds 2 attributes:

- confirmed : this is the one you need to check whether an account is confirmed or not. Once set to True, it is not expected to be set back to False.
Note that it is different from 'is_active' which is related to some other django behaviors.
- new_email : used by django_silly_auth for email change requests.

and 2 methods:

- get_jwt_token() -> jwt token: used by django_silly_auth
- verify_jwt_token() -> a user object or None: used by django_silly_auth

### 03 Settings and urls

**settings.py**
```python
INSTALLED_APPS = [
    # ...
    # 3rd party
    'rest_framework',
    'rest_framework.authtoken',
    'django_silly_auth',
]

# If used with Django Rest Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
}

AUTH_USER_MODEL = '<wherever is your model>.User'


## Site's email config
EMAIL_IS_CONFIGURED = False

if EMAIL_IS_CONFIGURED:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# for testing email easily and free: https://mailtrap.io/
EMAIL_HOST = "mail03.lwspanel.com"
EMAIL_HOST_USER = "no-reply@xxxxxx.fr"
EMAIL_HOST_PASSWORD = "xxxxxx"
EMAIL_PORT = 587
# TLS/SSL is better on if available, otherwise keep it off
EMAIL_USE_TLS = False

# Optionnal, here the given values are the default ones.
SILLY_AUTH = {
    # General settings
    "SITE_NAME": None,  # str used in templates if provided
    "GET_ALL_USERS": False,  # True for dev only
    "PRINT_WARNINGS": True,  # print warnings to terminal

    # emails settings
    "EMAIL_TERMINAL_PRINT": True,  # print emails to terminal
    "EMAIL_VALID_TIME": 600,  # seconds

    # login / logout
    "ALLOW_LOGIN_ENDPOINT": True,  # activate this endpoint
    "LOGIN_REDIRECT": None,
    "ALLOW_LOGOUT_ENDPOINT": True,  # activate this endpoint

    # account creation
    "ALLOW_CREATE_USER_ENDPOINT": True,  # activate this endpoint
    "ALLOW_EMAIL_CONFIRM_ENDPOINT": True,  # activate this endpoint (hook for email link)
    "EMAIL_SEND_ACCOUNT_CONFIRM_LINK": True,
    "ACCOUNT_CONFIRMED_REDIRECT": None,
    "EMAIL_CONFIRM_ACCOUNT_TEMPLATE":
        "silly_auth/emails/confirm_email.txt",

    # password reset (forgotten password)
    "ALLOW_RESET_PASSWORD_ENDPOINT": True,  # activate this endpoint
    "EMAIL_SEND_PASSWORD_RESET_LINK": True,
    "EMAIL_RESET_PASSWORD_TEMPLATE":
        "silly_auth/emails/request_password_reset.txt",
    #   default frontend are classic django views, you can change it to
    #   your own views and/or templates
    "RESET_PASSWORD_ENDPOINT": "auth/password/reset/",
    "RESET_PASSWORD_TEMPLATE": "silly_auth/reset_password.html",
    "RESET_PASSWORD_DONE_TEMPLATE": "silly_auth/reset_password_done.html",
    "RESET_PASSWORD_DONE_URL_TO_SITE": None,  # http:// link to site if provided


}

```
**urls.py**
```python

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('django_silly_auth.urls')),
]


```
You're good to go now !

<hr>

## Endpoints
'auth/' (or wherever you included django_silly_auth.urls) +

|Endpoint / SILLY_AUTH config | method | form-data | Permission | Effects |
|---|---|---|---|---|
ALLOW_LOGIN_ENDPOINT = True
| `token/login/` | POST | username, password | - | get a jwt token |
ALLOW_LOGOUT_ENDPOINT = True
| `token/logout/` | GET | - | IsAuthenticated | force delete token |
ALLOW_CREATE_USER_ENDPOINT
| `users/` | GET | - | - | if GET_ALL_USERS = True: get all users (use only for dev) |
| `users/` | POST | username, email, password | - | Create a new user |
ALLOW_EMAIL_CONFIRM_ENDPOINT = True
| `confirm_email/<token>/` | GET | - | - | activate from the email link, set user.confirmed to True |
RESET_PASSWORD_ENDPOINT = True
| `password/request_reset/` | POST | credential | - | send a reset email |
| `RESET_PASSWORD_ENDPOINT/<token>/` | GET | - | - | recieve the password reset token, change this endpoint for a SPA |
| `password/reset/done/` | GET | - | @login_required | confirm reset done with a template, not used if ALLOW_RESET_PASSWORD_ENDPOINT = False |
ALLOW_CHANGE_PASSWORD_ENDPOINT = True
| `password/change/` | POST | password, password2 | IsAuthenticated | Change the password |
ALLOW_CHANGE_EMAIL_ENDPOINT = True
| `email/request_change/` | POST | email | IsAuthenticated | Send a confirmation email for activating the new email |
| `` |  |  |  |  |
| `` |  |  |  |  |
| `` |  |  |  |  |
| `` |  |  |  |  |

## Autorization with jwt token
If `IsAuthenticated` is needed, add this in your headers:
```
key: Authorization

value: Token {the token}
```