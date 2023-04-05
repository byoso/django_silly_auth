from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

from django_silly_auth.config import SILLY_AUTH_SETTINGS as conf
from django_silly_auth.forms import NewPasswordForm, NewEmailConfirmForm
from django_silly_auth.templates.helpers import dsa_template_path


print("=== IMPORT django_silly_auth.views.views")

User = get_user_model()


def test_templates_view(request):
    users = User.objects.all()
    context = {
        "users": users,
        "title": "dsa render test",
        "base_template": conf["BASE_TEMPLATE"],
    }
    return render(request, dsa_template_path("silly_auth/_test/_test.html"), context)


def test_users_view(request):
    users = User.objects.all()
    context = {
        "users": users,
        "title": "dsa render test",
        "base_template": conf["BASE_TEMPLATE"],
    }
    return render(request, dsa_template_path("silly_auth/_test/_users.html"), context)


def reset_password(request, token):
    user = User.verify_jwt_token(token)
    if not user:
        return HttpResponse('error: invalid token')
    if request.method == 'POST':
        form = NewPasswordForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['password'])
            user.is_active = True
            user.save()
            context = {
                "link": conf["SITE_URL"],
                "base_template": conf["BASE_TEMPLATE"],
                "title": conf["TEMPLATES_TITLE"],
            }
            return render(request, conf["RESET_PASSWORD_DONE_TEMPLATE"], {'link': conf["SITE_URL"]})
        else:
            return render(request, conf["RESET_PASSWORD_TEMPLATE"], {'form': form})

    if user:
        if not user.is_confirmed:
            user.is_confirmed = True
            user.save()
        context = {
            "user": user,
            "site_name": conf["SITE_NAME"],
            "form": NewPasswordForm(),
            "base_template": conf["BASE_TEMPLATE"],
            "title": conf["TEMPLATES_TITLE"],
        }
        return render(request, conf["RESET_PASSWORD_TEMPLATE"], context)


def password_reset_done(request):
    context = {
        "site_name": conf["SITE_NAME"],
        "link": conf["SITE_URL"],
        "base_template": conf["BASE_TEMPLATE"],
        "title": conf["TEMPLATES_TITLE"],
    }
    return render(request, conf["RESET_PASSWORD_DONE_TEMPLATE"], context)


def confirm_new_email(request, token):
    """Recieves the token given by email and confirms the user's account"""
    if request.method == 'POST':
        user = User.verify_jwt_token(token)
        if user and user.new_email:
            form = NewEmailConfirmForm(request.POST)
            if form.is_valid():
                match = check_password(form.cleaned_data['password'], user.password)
                if match:
                    user.email = user.new_email
                    user.new_email = None
                    user.save()
                    context = {
                        "user": user,
                        "site_name": conf["SITE_NAME"],
                        "link": conf["SITE_URL"],
                        "base_template": conf["BASE_TEMPLATE"],
                        "title": conf["TEMPLATES_TITLE"],
                    }
                    return render(request, conf["NEW_EMAIL_CONFIRMED_DONE_TEMPLATE"], context)
                form.add_error('password', 'Invalid password')
            context = {
                "form": form,
                "user": user,
                "site_name": conf["SITE_NAME"],
                "base_template": conf["BASE_TEMPLATE"],
                "title": conf["TEMPLATES_TITLE"],
            }
            return render(request, conf["NEW_EMAIL_CONFIRM_TEMPLATE"], context)

    else:
        user = User.verify_jwt_token(token)
        if user and user.new_email:
            form = NewEmailConfirmForm()
            context = {
                "form": form,
                "user": user,
                "site_name": conf["SITE_NAME"],
                "base_template": conf["BASE_TEMPLATE"],
                "title": conf["TEMPLATES_TITLE"],
            }
            return render(request, conf["NEW_EMAIL_CONFIRM_TEMPLATE"], context)
    if conf["SITE_URL"]:
        return redirect(conf["SITE_URL"])
    return HttpResponse('error: invalid token or no email change ongoing')


def email_change_done(request):
    context = {
        "base_template": conf["BASE_TEMPLATE"],
        "title": conf["TEMPLATES_TITLE"],
    }
    return render(request, conf["NEW_EMAIL_CONFIRMED_DONE_TEMPLATE"], context)
