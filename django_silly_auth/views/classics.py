from django.http import HttpResponse, Http404
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _

from django_silly_auth.config import SILLY_AUTH_SETTINGS as conf
from django_silly_auth.forms import NewPasswordForm, NewEmailConfirmForm
from django_silly_auth.templates.helpers import dsa_template_path
from django_silly_auth.forms import (
    LoginForm,
    SignInForm,
    RequestPasswordResetForm,
    ResetPasswordForm,
    ChangeUsernameForm,
    ChangeEmailForm,
)
from django_silly_auth.utils import (
    send_password_reset_email,
    send_confirm_email,
)

print("=== IMPORT django_silly_auth.views.classics")

User = get_user_model()


def index(request):
    context = {
        "base_template": conf["BASE_TEMPLATE"],
        "title": conf["TEMPLATES_TITLE"],
    }
    return render(request, conf["CLASSIC_INDEX"], context)


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            credential = form.cleaned_data['credential']
            password = form.cleaned_data['password']
            if "@" in credential:
                username = User.objects.get(email=credential).username
                user = authenticate(
                    request, username=username, password=password)
            else:
                user = authenticate(
                    request, username=credential, password=password)
            if user is not None:
                login(request, user)
                return redirect('classic_index')
            else:
                messages.add_message(
                    request, messages.ERROR,
                    message=_("Access denied: wrong password"),
                    extra_tags="danger"),
        else:
            context = {
                "form": form,
                "base_template": conf["BASE_TEMPLATE"],
                "title": conf["TEMPLATES_TITLE"],
            }
            return render(request, conf["CLASSIC_LOGIN"], context)

    form = LoginForm()
    context = {
        "form": form,
        "base_template": conf["BASE_TEMPLATE"],
        "title": conf["TEMPLATES_TITLE"],
    }
    return render(request, conf["CLASSIC_LOGIN"], context)


def logout_view(request):
    logout(request)
    return redirect('classic_index')


@login_required
def account(request):
    context = {
        "base_template": conf["BASE_TEMPLATE"],
        "title": conf["TEMPLATES_TITLE"],
    }
    return render(request, conf["CLASSIC_ACCOUNT"], context)


def signin_view(request):
    if request.method == 'POST':
        form = SignInForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User(username=username, email=email, is_active=False)
            user.set_password(password)
            user.save()
            send_password_reset_email(request, user)
            return redirect('classic_login')
        else:
            context = {
                "form": form,
                "base_template": conf["BASE_TEMPLATE"],
                "title": conf["TEMPLATES_TITLE"],
            }
            return render(request, conf["CLASSIC_SIGNIN"], context)

    form = SignInForm()
    context = {
        "form": form,
        "base_template": conf["BASE_TEMPLATE"],
        "title": conf["TEMPLATES_TITLE"],
    }
    return render(request, conf["CLASSIC_SIGNIN"], context)


def request_password_reset(request):
    if request.method == "POST":
        form = RequestPasswordResetForm(request.POST)
        if form.is_valid():
            credential = form.cleaned_data['credential']
            if "@" in credential:
                user = User.objects.get(email=credential)
            else:
                user = User.objects.get(username=credential)

            # user existence is checked by the form validation #
            send_password_reset_email(request, user)

            messages.add_message(
                request, messages.INFO,
                message=(_(
                    f"Please check your email '{user.email}' "
                    "to reset your password"
                    )),
                extra_tags="info"
            )
        else:
            context = {
                "form": form,
                "base_template": conf["BASE_TEMPLATE"],
                "title": conf["TEMPLATES_TITLE"],
            }
            return render(
                request,
                conf["CLASSIC_REQUEST_PASSWORD_RESET"],
                context
                )
    form = RequestPasswordResetForm()
    if request.user.is_authenticated:
        form = RequestPasswordResetForm(initial={'credential': request.user.email})
    context = {
        "form": form,
        "base_template": conf["BASE_TEMPLATE"],
        "title": conf["TEMPLATES_TITLE"],
    }
    return render(request, conf["CLASSIC_REQUEST_PASSWORD_RESET"], context)


def reset_password(request, token):
    user = User.verify_jwt_token(token)
    if user is None:
        return HttpResponse(_("Token invalid or expired"))

    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['password'])
            user.is_active = True
            user.is_confirmed = True
            user.save()
            login(request, user)
            messages.add_message(
                request, messages.SUCCESS,
                message=_("Your password have been reset"),
                extra_tags="success"
            )
            return redirect('classic_account')
        else:
            context = {
                'form': form,
                "base_template": conf["BASE_TEMPLATE"],
                "title": conf["TEMPLATES_TITLE"],
            }
            return render(request, conf["CLASSIC_RESET_PASSWORD"], context)
    form = ResetPasswordForm()
    context = {
        'user': user,
        'form': form,
        "base_template": conf["BASE_TEMPLATE"],
        "title": conf["TEMPLATES_TITLE"],
    }
    return render(request, conf["CLASSIC_RESET_PASSWORD"], context)


@login_required
def change_username(request):
    if request.method == 'POST':
        form = ChangeUsernameForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            user = request.user
            user.username = username
            user.save()
            messages.add_message(
                request, messages.SUCCESS,
                message=_(f"New username set: '{username}'"),
                extra_tags="success"
            )
            return redirect("classic_account")
        else:
            context = {
                'form': form,
                "base_template": conf["BASE_TEMPLATE"],
                "title": conf["TEMPLATES_TITLE"],
            }
            return render(
                request,
                conf["CLASSIC_CHANGE_USERNAME"],
                context,
                )

    form = ChangeUsernameForm()
    context = {
        'form': form,
        "base_template": conf["BASE_TEMPLATE"],
        "title": conf["TEMPLATES_TITLE"],
    }
    return render(request, conf["CLASSIC_CHANGE_USERNAME"], context)


@login_required
def change_email(request):
    if request.method == 'POST':
        form = ChangeEmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = request.user
            user.unconfirmed_email = email
            user.save()
            send_confirm_email(request, user)

            messages.add_message(
                request, messages.INFO,
                message=(_(
                    "Please check your email to"
                    f" confirm your address '{email}'"
                    )),
                extra_tags="info"
            )
        else:
            context = {
                'form': form,
                "base_template": conf["BASE_TEMPLATE"],
                "title": conf["TEMPLATES_TITLE"],
            }
            return render(request, conf["CLASSIC_CHANGE_EMAIL"], context)

    form = ChangeEmailForm()
    context = {
        'form': form,
        "base_template": conf["BASE_TEMPLATE"],
        "title": conf["TEMPLATES_TITLE"],
    }
    return render(request, conf["CLASSIC_CHANGE_EMAIL"], context)


def confirm_email(request, token):
    user = User.verify_jwt_token(token)
    if user is not None:
        user.email = user.new_email
        user.new_email = None
        user.is_confirmed = True
        user.save()
        login(request, user)
        messages.add_message(
            request, messages.SUCCESS,
            message=_(f"Your new email have been confirmed: '{user.email}'"),
            extra_tags="success"
        )

        return redirect("classic_account")
