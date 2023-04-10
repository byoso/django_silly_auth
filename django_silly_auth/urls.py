from django.urls import path
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from django_silly_auth.config import SILLY_AUTH_SETTINGS as conf
from django_silly_auth.views import (
    api_views,
    test_views,
    silly_views,
    classics)


if conf["VERBOSE"]:
    print("=== DSA IMPORT django_silly_auth.urls")
    if conf["USE_DRF"]:
        print("=== DSA login_with_auth_token FROM django_silly_auth.views.api_custom_login")

if conf["USE_DRF"]:
    from django_silly_auth.views.api_custom_login import (
        LoginWithAuthToken,
        LoginWithJWTToken,
    )

prefix = conf["DSA_PREFIX"]
User = get_user_model()


# Signal interceptor to make sure that superusers are always active
@receiver(pre_save, sender=User)
def new_superuser_is_always_active(sender, instance, **kwargs):
    if instance.is_superuser and not instance.is_confirmed:
        instance.is_confirmed = True
        instance.is_active = True


urlpatterns = []

# DRF routes
if conf["USE_DRF"]:
    urlpatterns += [
        path(f'{prefix}token/login/', LoginWithAuthToken.as_view(), name="login_with_auth_token"),
        path(f'{prefix}token/logout/', api_views.logout_api_view, name="logout_api_view"),
        path(
            f'{prefix}password/request_reset/',
            api_views.request_password_reset,
            name='request_password_reset'
        ),
        path(
            f'{prefix}email/confirm_email/resend/',
            api_views.resend_email_confirmation,
            name="resend_email_confirmation"
        ),
        path(
            f'{prefix}password/change/',
            api_views.change_password,
            name='change_password'
        ),
        path(
            f'{prefix}email/request_change/',
            api_views.change_email_request,
            name='change_email_request'
        ),
        ]

    if conf["ALLOW_CREATE_USER_ENDPOINT"]:
        urlpatterns += [path(f'{prefix}users/', api_views.UserView.as_view(), name="users")]


# Classic routes

if conf["USE_CLASSIC"]:
    urlpatterns += [
        path(f'{prefix}classic_login/', classics.login_view, name='classic_login'),
        path(f'{prefix}classic_logout/', classics.logout_view, name='classic_logout'),
        path(f'{prefix}classic_signup/', classics.signup_view, name='classic_signup'),
        path(f'{prefix}classic_change_username/', classics.change_username, name='classic_change_username'),
        path(f'{prefix}classic_change_email/', classics.change_email, name='classic_change_email'),
        path(f'{prefix}classic_confirm_email/<token>', classics.confirm_email, name='classic_confirm_email'),
        path(
            f'{prefix}classic_request_resend_confirmation_email/',
            classics.request_resend_account_confirmation_email,
            name='classic_request_resend_confirmation_email'
        ),
        path(
            f'{prefix}classic_reset_password/',
            classics.reset_password,
            name='classic_reset_password_authenticated'
        ),
    ]
    if conf["USE_CLASSIC_INDEX"]:
        urlpatterns += [path('', classics.index, name='classic_index'), ]
    if conf["USE_CLASSIC_ACCOUNT"]:
        urlpatterns += [path(f'{prefix}classic_account/', classics.account, name='classic_account'), ]

# Email Confirmation routes

if conf['CONFIRMATION_METHOD'] == 'GET':  # uses the classic views, not the 'good' way for a SPA, but works.
    urlpatterns += [
        path(f'{prefix}classic_reset_password/<token>', classics.reset_password, name='classic_reset_password'),
        path(f'{prefix}classic_request_password_reset/', classics.request_password_reset, name='classic_request_password_reset'),
    ]
    if conf["USE_SILLY"]:
        urlpatterns += [
            path(
                f'{prefix}dsa_confirm_email/<token>',
                silly_views.silly_confirm_email,
                name='silly_confirm_email'),
            path(
                f'{prefix}dsa_password_reset_done',
                silly_views.silly_password_reset_done,
                name='silly_password_reset_done'),
        ]

if conf['CONFIRMATION_METHOD'] == 'POST':
    urlpatterns += [
        path(f'{prefix}login_with_jwt/', LoginWithJWTToken.as_view(), name="login_with_jwt_token"),
    ]

# testing routes
if conf["TEST_TEMPLATES"]:
    urlpatterns += [
        path(f'{prefix}_test/', test_views.test_templates_view, name="test_templates_view"),
        path(f'{prefix}_test_users/', test_views.test_users_view, name="test_users_view"),
        ]
