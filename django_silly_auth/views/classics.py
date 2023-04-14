from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.db import transaction

from django_silly_auth.config import SILLY_AUTH_SETTINGS as conf
from django_silly_auth.forms import (
    LoginForm,
    SignUpForm,
    CredentialForm,
    ResetPasswordForm,
    ChangeUsernameForm,
    ChangeEmailForm,
)
from django_silly_auth.utils import (
    send_password_reset_email,
    send_confirm_email,
    delete_unconfirmed,
)

if conf["VERBOSE"]:
    print("=== DSA IMPORT django_silly_auth.views.classics")

User = get_user_model()


@transaction.atomic
def index(request):
    context = {
        "base_template": conf["BASE_TEMPLATE"],
        "title": conf["TEMPLATES_TITLE"],
    }
    return render(request, conf["CLASSIC_INDEX"], context)

@transaction.atomic
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
            if user is not None and user.is_confirmed:
                login(request, user)
                return redirect('classic_index')
            else:
                messages.add_message(
                    request, messages.ERROR,
                    message=_("Incorrect credentials or unconfirmed account."),
                    extra_tags="warning"),
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


@transaction.atomic
@login_required
def account(request):
    context = {
        "base_template": conf["BASE_TEMPLATE"],
        "title": conf["TEMPLATES_TITLE"],
    }
    return render(request, conf["CLASSIC_ACCOUNT"], context)


@transaction.atomic
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User(username=username, email=email, is_active=True)
            user.set_password(password)
            user.save()
            send_confirm_email(request, user)
            delete_unconfirmed(user)

            message1 = _(
                "Please check your inbox at"
                " '%(email)s' to confirm your account."
            ) % {'email': user.email}
            message2 = ""
            if conf["DELETE_UNCONFIRMED_TIME"] != 0.0:

                message2 = _(
                    " If you do not confirm your account within the next "
                    "%(time)s hours, it will be deleted."
                ) % {'time': conf['DELETE_UNCONFIRMED_TIME']}

            message = "%(message1)s%(message2)s" % {
                'message1': message1,
                'message2': message2,
            }

            messages.add_message(
                request, messages.INFO,
                message=message,
                extra_tags="info"
            )
            return redirect('classic_login')
        else:
            context = {
                "form": form,
                "base_template": conf["BASE_TEMPLATE"],
                "title": conf["TEMPLATES_TITLE"],
            }
            return render(request, conf["CLASSIC_SIGNUP"], context)

    form = SignUpForm()
    context = {
        "form": form,
        "base_template": conf["BASE_TEMPLATE"],
        "title": conf["TEMPLATES_TITLE"],
    }
    return render(request, conf["CLASSIC_SIGNUP"], context)


@transaction.atomic
def request_password_reset(request):
    if request.method == "POST":
        form = CredentialForm(request.POST)
        if form.is_valid():
            credential = form.cleaned_data['credential']
            if "@" in credential:
                user = User.objects.get(email=credential)
            else:
                user = User.objects.get(username=credential)
            # user existence is checked by the form validation #
            if user.is_active:
                messages.add_message(
                    request, messages.INFO,
                    message=(_(
                        "Please check your inbox "
                        "and follow the instructions "
                        "to reset your password."
                        )),
                    extra_tags="info"
                )
                send_password_reset_email(request, user)

            else:
                messages.add_message(
                    request, messages.INFO,
                    message=(_(
                        "Your account is no longer active. Please contact the administrator. "
                        "No email has been sent."
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
    form = CredentialForm()
    if request.user.is_authenticated:
        form = CredentialForm(initial={'credential': request.user.email})
    context = {
        "form": form,
        "base_template": conf["BASE_TEMPLATE"],
        "title": conf["TEMPLATES_TITLE"],
    }
    return render(request, conf["CLASSIC_REQUEST_PASSWORD_RESET"], context)


@transaction.atomic
def reset_password(request, token=None):
    """Receive the token from the confirmation email and reset the password
    or already authenticated user.
    """
    if token:
        user = User.verify_jwt_token(token)
    elif request.user.is_authenticated:
        user = request.user
    else:
        user = None

    if user is None:
        messages.add_message(
            request, messages.INFO,
            message=(_(
                "Token invalid or expired"
                )),
            extra_tags="danger"
        )
        return redirect('classic_index')

    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['password'])
            user.save()
            if conf["USE_SILLY"]:
                return redirect('dsa_password_reset_done')
            login(request, user)
            messages.add_message(
                request, messages.SUCCESS,
                message=_("Your password has been successfully reset. Please log in."),
                extra_tags="success"
            )
            return redirect('classic_index')
        else:
            context = {
                'form': form,
                "base_template": conf["BASE_TEMPLATE"],
                "title": conf["TEMPLATES_TITLE"],
            }
            return render(request, conf["CLASSIC_RESET_PASSWORD"], context)

    form = ResetPasswordForm()
    login(request, user)
    if token:
        messages.add_message(
            request, messages.SUCCESS,
            message=_("You have been logged in via email confirmation. Please reset your password."),
            extra_tags="warning"
        )

    context = {
        'form': form,
        "base_template": conf["BASE_TEMPLATE"],
        "title": conf["TEMPLATES_TITLE"],
    }
    return render(request, conf["CLASSIC_RESET_PASSWORD"], context)


@transaction.atomic
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
                message=_(
                    "New username set: '%(username)s'."
                ) % {'username': username},
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


@transaction.atomic
@login_required
def change_email(request):
    if request.method == 'POST':
        form = ChangeEmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = request.user
            user.new_email = email
            user.save()
            send_confirm_email(request, user)

            message = _(
                "Please check your inbox to confirm your new "
                "address at '%(email)s'") % {"email": user.new_email}
            messages.add_message(
                request, messages.INFO,
                message,
                extra_tags="info"
            )
            return redirect("classic_account")
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


@transaction.atomic
def confirm_email(request, token):
    user = User.verify_jwt_token(token)
    if user is None:
        messages.add_message(
            request, messages.INFO,
            message=(_(
                "Token invalid or expired"
                )),
            extra_tags="danger"
        )
        return redirect('classic_index')
    if user is not None and user.is_active:
        if not user.is_confirmed:
            user.is_confirmed = True
            user.new_email = None
            msg = _("Your account has been confirmed.")
            user.save()
        elif user.new_email:
            user.email = user.new_email
            user.new_email = None
            msg = _("Your new email has been confirmed.")
            user.save()
        else:
            msg = _("Your account is already confirmed.")
        messages.add_message(
            request, messages.SUCCESS,
            message=msg,
            extra_tags="success"
        )

        return redirect("classic_index")


@transaction.atomic
def request_resend_account_confirmation_email(request):
    if request.method == 'POST':
        form = CredentialForm(request.POST)
        if form.is_valid():
            credential = form.cleaned_data['credential']
            if "@" in credential:
                user = User.objects.get(email=credential)
            else:
                user = User.objects.get(username=credential)

            # user existence is checked by the form validation #

            if user.is_confirmed:
                messages.add_message(
                    request, messages.INFO,
                    message=(_(
                        "Your account is already confirmed. "
                        "No email has been sent."
                        )),
                    extra_tags="info"
                )
                return redirect("classic_login")

            send_confirm_email(request, user)

            messages.add_message(
                request, messages.INFO,
                message=(_(
                    "Please check your inbox "
                    "to confirm your account."
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
                conf["CLASSIC_REQUEST_RESEND_ACCOUNT_CONFIRMATION_EMAIL"],
                context
                )
    form = CredentialForm()
    context = {
        "form": form,
        "base_template": conf["BASE_TEMPLATE"],
        "title": conf["TEMPLATES_TITLE"],
    }
    return render(
        request,
        conf["CLASSIC_REQUEST_RESEND_ACCOUNT_CONFIRMATION_EMAIL"],
        context
        )
