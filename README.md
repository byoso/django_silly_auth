# Django Silly Auth (WIP)

## Why one more authentication system for Django and DRF? again !

I've used a few ones, and did not find the one that behaves the way I want,
efficient, but flexible, I want to win time, and get what I need straight to the point.

The aim of DSA it to provide a good-enought-to-go authentication out of the box, but still remains highly
modulable throught its SILLY_AUTH config in **settings.py**, so it is always possible to improve your
authentication when you have the time for it.

If you're building a SPA, you can go with DSA as it is at first, and as your work progresses,
switch off the default urls, views and templates to add yours.


## DRF only (for now)

Currently only works with Django Rest Framework, not with classic Django.

## [installation](https://github.com/byoso/django_silly_auth/wiki/Installation)

<hr>

## Endpoints
'auth/' (or wherever you included django_silly_auth.urls) +

|Endpoint / SILLY_AUTH config | method | form-data | Permission | Effects |
|---|---|---|---|---|
ALLOW_LOGIN_ENDPOINT = True
| `token/login/` | POST | credential, password | - | get a jwt token |
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
| `email/change/done/` | GET |  |  | Displays a confirmation template |
| `` |  |  |  |  |
| `` |  |  |  |  |
| `` |  |  |  |  |

## Credential
`credential` is a field that expects an email OR a username, both can match as well.

## Autorization with jwt token
If `IsAuthenticated` is needed, add this in your headers:
```
key: Authorization

value: Token {the token}
```