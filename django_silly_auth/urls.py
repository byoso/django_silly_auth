from django.urls import path
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from django_silly_auth.config import SILLY_AUTH_SETTINGS as conf
from django_silly_auth.views import api_views, views, classics

if conf["USE_DRF"]:
    from django_silly_auth.views.api_custom_login import login_with_auth_token
    print("=== login_with_auth_token FROM django_silly_auth.api_custom_login")

print("=== IMPORT django_silly_auth.urls")

User = get_user_model()


# Signal interceptor to make sure that superusers are always active
@receiver(pre_save, sender=User)
def new_superuser_is_always_active(sender, instance, **kwargs):
    if instance.is_superuser and not instance.is_confirmed:
        instance.is_confirmed = True
        instance.is_active = True


urlpatterns = [
]
# for testing
if conf["TEST_TEMPLATES"]:
    urlpatterns += [
        path('_test/', views.test_templates_view, name="test_templates_view"),
        path('_test_users/', views.test_users_view, name="test_users_view"),
        ]

if conf["USE_DRF"]:

    if conf["ALLOW_CREATE_USER_ENDPOINT"]:
        urlpatterns += [path('users/', api_views.UserView.as_view(), name="users")]
    if conf["ALLOW_LOGIN_ENDPOINT"]:
        urlpatterns += [path('token/login/', login_with_auth_token, name="login_with_auth_token")]
    if conf["ALLOW_LOGOUT_ENDPOINT"]:
        urlpatterns += [path('token/logout/', api_views.logout_api_view, name="logout_api_view")]
    if conf["ALLOW_EMAIL_CONFIRM_ENDPOINT"]:
        urlpatterns += [
            # hook for email confirmation
            path(
                'confirm_email/<token>/',
                api_views.confirm_email,
                name='confirm_email'),
            # resend email confirmation
            path(
                'email/confirm_email/resend/',
                api_views.resend_email_confirmation,
                name="resend_email_confirmation"
            )
        ]
    if conf["ALLOW_RESET_PASSWORD_ENDPOINT"]:
        urlpatterns += [
            path(
                'password/request_reset/',
                api_views.request_password_reset,
                name='request_password_reset'
            ),
            # hook for email reset password
            path(
                conf["RESET_PASSWORD_ENDPOINT"] + '<token>/',
                views.reset_password,
                name='reset_password'
            ),
            path(
                'password/reset/done/',
                views.password_reset_done,
                name='password_reset_done'
            )

        ]

    if conf["ALLOW_CHANGE_PASSWORD_ENDPOINT"]:
        urlpatterns += [
            path(
                'password/change/',
                api_views.change_password,
                name='change_password'
            ),
        ]

    if conf["ALLOW_CHANGE_EMAIL_ENDPOINT"]:
        urlpatterns += [
            path(
                'email/request_change/',
                api_views.change_email_request,
                name='change_email_request'
            ),
        ]

if conf["ALLOW_CONFIRM_NEW_EMAIL_HOOK_ENDPOINT"]:
    urlpatterns += [
        # hook for new email confirmation
        path(
            'confirm_new_email/<token>/',
            views.confirm_new_email,
            name='confirm_new_email'),

        path(
            'email/change/done/',
            views.email_change_done,
            name='email_change_done'
        )
    ]

if conf["FULL_CLASSIC"]:
    urlpatterns += [
        path('classic_login/', classics.login_view, name='classic_login'),
        path('classic_logout/', classics.logout_view, name='classic_logout'),
        path('classic_signup/', classics.signup_view, name='classic_signup'),
        path('classic_request_password_reset/', classics.request_password_reset, name='classic_request_password_reset'),
        path('classic_reset_password/<token>', classics.reset_password, name='classic_reset_password'),
        path('classic_change_username/', classics.change_username, name='classic_change_username'),
        path('classic_change_email/', classics.change_email, name='classic_change_email'),
        path('classic_confirm_email/<token>', classics.confirm_email, name='classic_confirm_email'),
        path(
            'classic_request_resend_confirmation_email/',
            classics.request_resend_account_confirmation_email,
            name='classic_request_resend_confirmation_email'
        ),
    ]
    if conf["USE_CLASSIC_INDEX"]:
        urlpatterns += [path('', classics.index, name='classic_index'),]
    if conf["USE_CLASSIC_ACCOUNT"]:
        urlpatterns += [path('classic_account/', classics.account, name='classic_account'),]
