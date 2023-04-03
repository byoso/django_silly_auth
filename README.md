# Django Silly Auth

## DRF only

Currently only works with Django Rest Framework, not with classic Django.

## [installation](https://github.com/byoso/django_silly_auth/wiki/Installation)

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
| `password/reset/done/` | GET | - | - | confirm reset done with a template, not used if ALLOW_RESET_PASSWORD_ENDPOINT = False |
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