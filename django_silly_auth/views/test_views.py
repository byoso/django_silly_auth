from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.db import transaction

from django_silly_auth.config import SILLY_AUTH_SETTINGS as conf

if conf["VERBOSE"]:
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
