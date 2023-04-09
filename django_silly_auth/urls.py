from django.urls import path
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from django_silly_auth import SILLY_AUTH_SETTINGS as conf
from django_silly_auth.views import api_views, test_views, classics

import django_silly_auth

if django_silly_auth.VERBOSE:
    print("=== DSA IMPORT django_silly_auth.urls")
    if conf["USE_DRF"]:
        print("=== DSA login_with_auth_token FROM django_silly_auth.views.api_custom_login")

if conf["USE_DRF"]:
    from django_silly_auth.views.api_custom_login import (
        LoginWithAuthToken,
        LoginWithJWTToken,
        # login_with_jwt_token,
    )

User = get_user_model()


# Signal interceptor to make sure that superusers are always active
@receiver(pre_save, sender=User)
def new_superuser_is_always_active(sender, instance, **kwargs):
    if instance.is_superuser and not instance.is_confirmed:
        instance.is_confirmed = True
        instance.is_active = True


urlpatterns = [
]
# DRF routes

if conf["USE_DRF"]:
    urlpatterns += [
        path('token/login/', LoginWithAuthToken.as_view(), name="login_with_auth_token"),
        path('token/logout/', api_views.logout_api_view, name="logout_api_view"),
        path(
            'password/request_reset/',
            api_views.request_password_reset,
            name='request_password_reset'
        ),
        path(
            'email/confirm_email/resend/',
            api_views.resend_email_confirmation,
            name="resend_email_confirmation"
        ),
        path(
            'password/change/',
            api_views.change_password,
            name='change_password'
        ),
        path(
            'email/request_change/',
            api_views.change_email_request,
            name='change_email_request'
        ),
        ]

    if conf["ALLOW_CREATE_USER_ENDPOINT"]:
        urlpatterns += [path('users/', api_views.UserView.as_view(), name="users")]


# Classic routes

if conf["USE_CLASSIC"]:
    urlpatterns += [
        path('classic_login/', classics.login_view, name='classic_login'),
        path('classic_logout/', classics.logout_view, name='classic_logout'),
        path('classic_signup/', classics.signup_view, name='classic_signup'),
        path('classic_request_password_reset/', classics.request_password_reset, name='classic_request_password_reset'),
        path('classic_change_username/', classics.change_username, name='classic_change_username'),
        path('classic_change_email/', classics.change_email, name='classic_change_email'),
        path(
            'classic_request_resend_confirmation_email/',
            classics.request_resend_account_confirmation_email,
            name='classic_request_resend_confirmation_email'
        ),
    ]
    if conf["USE_CLASSIC_INDEX"]:
        urlpatterns += [path('', classics.index, name='classic_index'), ]
    if conf["USE_CLASSIC_ACCOUNT"]:
        urlpatterns += [path('classic_account/', classics.account, name='classic_account'), ]


# Email Confirmation routes

if conf['CONFIRMATION_METHOD'] == 'GET':  # uses the classic views, not the 'good' way for a SPA, but works.
    urlpatterns += [
        path('classic_reset_password/<token>', classics.reset_password, name='classic_reset_password'),
        path('classic_confirm_email/<token>', classics.confirm_email, name='classic_confirm_email'),
    ]

if conf['CONFIRMATION_METHOD'] == 'POST':
    urlpatterns += [
        path('login_with_jwt/', LoginWithJWTToken.as_view(), name="login_with_jwt_token" ),
    ]

# testing routes
if conf["TEST_TEMPLATES"]:
    urlpatterns += [
        path('_test/', test_views.test_templates_view, name="test_templates_view"),
        path('_test_users/', test_views.test_users_view, name="test_users_view"),
        ]
