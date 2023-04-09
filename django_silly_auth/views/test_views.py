from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.db import transaction

from django_silly_auth import SILLY_AUTH_SETTINGS as conf
from django_silly_auth.forms import NewPasswordForm, NewEmailConfirmForm
import django_silly_auth

if django_silly_auth.VERBOSE:
    print("=== DSA IMPORT django_silly_auth.views.views")

"""Here are the views that are non-api but can be used alongside an api site, with
 SILLY_AUTH['CONFIRMATION_METHOD'] = 'GET'

"""


User = get_user_model()


@transaction.atomic
def test_templates_view(request):
    users = User.objects.all()
    context = {
        "users": users,
        "title": "dsa render test",
        "base_template": conf["BASE_TEMPLATE"],
    }
    return render(request, "silly_auth/_test/_test.html", context)


@transaction.atomic
def test_users_view(request):
    users = User.objects.all()
    context = {
        "users": users,
        "title": "dsa render test",
        "base_template": conf["BASE_TEMPLATE"],
    }
    return render(request, "silly_auth/_test/_users.html", context)
