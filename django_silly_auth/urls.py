from django.urls import path
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from django_silly_auth.config import SILLY_AUTH_SETTINGS as conf
from django_silly_auth.views import (
    api_views,
    try_views,
    silly_views,
    classics)


if conf["VERBOSE"]:
    print("=== DSA IMPORT django_silly_auth.urls")
    if conf["USE_DRF"]:
        print("=== DSA LoginWithAuthToken FROM django_silly_auth.views.api_custom_login")

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
        path(f'{prefix}token/login/', api_views.LoginWithAuthToken.as_view(), name="token_login"),
        path(f'{prefix}token/logout/', api_views.token_logout, name="token_logout"),
        path(
            f'{prefix}password/request_reset/',
            api_views.password_request_reset,
            name='password_request_reset'
        ),
        path(
            f'{prefix}email/confirm_email/resend/',
            api_views.email_confirm_email_resend,
            name="email_confirm_email_resend"
        ),
        path(
            f'{prefix}password/change/',
            api_views.password_change,
            name='password_change'
        ),
        path(
            f'{prefix}email/request_change/',
            api_views.email_request_change,
            name='email_request_change'
        ),
        ]

    if conf['ALLOW_CHANGE_USERNAME']:
        urlpatterns += [
            path(
                f'{prefix}username/change/',
                api_views.username_change,
                name='username_change'
            ),
        ]

    if conf["ALLOW_DELETE_ME_ENDPOINT"]:
        urlpatterns += [
            path(f'{prefix}users/delete_me/', api_views.users_delete_me, name='users_delete_me'),
        ]

    if conf["ALLOW_CREATE_USER_ENDPOINT"]:
        urlpatterns += [path(f'{prefix}users/', api_views.UserView.as_view(), name="users")]

    if conf['ALLOW_MY_INFOS_ENDPOINT']:
        urlpatterns += [path(f'{prefix}users/my_infos/', api_views.users_my_infos, name="users_my_infos")]

    if conf["ALLOW_GET_ALL_USERS"]:
        urlpatterns += [path(f'{prefix}users/all/', api_views.get_users_all, name="get_users_all")]

# Classic routes

if conf["USE_CLASSIC"]:
    urlpatterns += [
        path(f'{prefix}classic_login/', classics.login_view, name='classic_login'),
        path(f'{prefix}classic_logout/', classics.logout_view, name='classic_logout'),
        path(f'{prefix}classic_signup/', classics.signup_view, name='classic_signup'),
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
    if conf["ALLOW_CHANGE_USERNAME"]:
        urlpatterns += [
            path(
                f'{prefix}classic_change_username/',
                classics.change_username,
                name='classic_change_username'
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
                silly_views.dsa_confirm_email,
                name='dsa_confirm_email'),
            path(
                f'{prefix}dsa_password_reset_done',
                silly_views.dsa_password_reset_done,
                name='dsa_password_reset_done'),
        ]

if conf['CONFIRMATION_METHOD'] == 'POST' or conf['AUTO_SET'] == 'TEST':
    urlpatterns += [
        path(f'{prefix}login_with_jwt/', api_views.LoginWithJWTToken.as_view(), name="login_with_jwt"),
    ]

# trying routes
if conf["TRY_TEMPLATES"] or conf['AUTO_SET'] == 'TEST':
    urlpatterns += [
        path(f'{prefix}_try/', try_views.try_templates_view, name="try_templates_view"),
        path(f'{prefix}_try_users/', try_views.try_users_view, name="try_users_view"),
        ]
